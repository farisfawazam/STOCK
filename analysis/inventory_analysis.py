import json
from collections import defaultdict, Counter
from dataclasses import dataclass
from datetime import datetime, date
from pathlib import Path
from typing import Dict, List, Tuple, Iterable

MAIN_WAREHOUSE = "VENUS"
DATE_FMT = "%Y-%m-%d"

def load_data(path: Path) -> Dict[str, List[dict]]:
    with path.open(encoding="utf-8") as f:
        return json.load(f)


def parse_date(value: str) -> date:
    return datetime.strptime(value, DATE_FMT).date()


@dataclass
class ItemInfo:
    code: str
    name: str
    qty_per_dus: int
    opening: int
    fisik: int
    ket: str


def build_item_index(stock_rows: Iterable[dict]) -> Dict[str, ItemInfo]:
    index: Dict[str, ItemInfo] = {}
    for row in stock_rows:
        info = ItemInfo(
            code=row["KODE BARANG"],
            name=row["NAMA BARANG"],
            qty_per_dus=int(row["QTY PER 1 DUS"]),
            opening=int(row["STOCK AWAL"]),
            fisik=int(row.get("FISIK", 0) or 0),
            ket=str(row.get("KET", "")).strip() or "-",
        )
        index[info.name] = info
    return index


def aggregate_movements(data: Dict[str, List[dict]], item_index: Dict[str, ItemInfo]):
    inbound_breakdown: Dict[str, Counter] = {name: Counter() for name in item_index}
    outbound_breakdown: Dict[str, Counter] = {name: Counter() for name in item_index}

    daily_in = defaultdict(lambda: Counter())
    daily_out = defaultdict(lambda: Counter())
    weekly_in = defaultdict(lambda: Counter())
    weekly_out = defaultdict(lambda: Counter())

    def record(counter_map, d: date, item: str, qty: int):
        counter_map[d][item] += qty

    def record_week(counter_map, d: date, item: str, qty: int):
        iso_year, iso_week, _ = d.isocalendar()
        counter_map[(iso_year, iso_week)][item] += qty

    def handle_in(item: str, qty: int, movement_type: str, movement_date: date):
        inbound_breakdown[item][movement_type] += qty
        record(daily_in, movement_date, item, qty)
        record_week(weekly_in, movement_date, item, qty)

    def handle_out(item: str, qty: int, movement_type: str, movement_date: date):
        outbound_breakdown[item][movement_type] += qty
        record(daily_out, movement_date, item, qty)
        record_week(weekly_out, movement_date, item, qty)

    for row in data.get("BARANG MASUK", []):
        item = row["NAMA BARANG"]
        if item not in item_index:
            continue
        qty = int(row.get("JUMLAH BARANG MASUK", 0) or 0)
        movement_date = parse_date(row["TANGGAL"])
        handle_in(item, qty, "MRD", movement_date)

    for row in data.get("ADJUST IN", []):
        item = row["NAMA BARANG"]
        if item not in item_index:
            continue
        qty = int(row.get("JUMLAH BARANG MASUK", 0) or 0)
        movement_date = parse_date(row["TANGGAL"])
        handle_in(item, qty, "ADJUST_IN", movement_date)

    for row in data.get("BARANG KELUAR", []):
        item = row["NAMA PRODUK"]
        if item not in item_index:
            continue
        qty = int(row.get("JUMLAH BARANG KELUAR", 0) or 0)
        movement_date = parse_date(row["TANGGAL"])
        handle_out(item, qty, "FILLING", movement_date)

    for row in data.get("ADJUST OUT", []):
        item = row["NAMA BARANG"]
        if item not in item_index:
            continue
        qty = int(row.get("JUMLAH BARANG KELUAR", 0) or 0)
        movement_date = parse_date(row["TANGGAL"])
        handle_out(item, qty, "ADJUST_OUT", movement_date)

    tw_recap: Dict[Tuple[str, str, str], Counter] = defaultdict(Counter)

    for row in data.get("TW", []):
        item = row["NAMA BARANG"]
        if item not in item_index:
            continue
        qty = int(row.get("JUMLAH BARANG KELUAR", 0) or 0)
        movement_date = parse_date(row["TANGGAL"])
        ket = row.get("KET", "")
        origin, destination = parse_origin_destination(ket)
        tw_recap[(item, origin, destination)]["qty"] += qty
        tw_recap[(item, origin, destination)]["count"] += 1
        if origin.upper() == MAIN_WAREHOUSE:
            handle_out(item, qty, "TW_OUT", movement_date)
        if destination.upper() == MAIN_WAREHOUSE:
            handle_in(item, qty, "TW_IN", movement_date)

    return {
        "inbound": inbound_breakdown,
        "outbound": outbound_breakdown,
        "daily_in": daily_in,
        "daily_out": daily_out,
        "weekly_in": weekly_in,
        "weekly_out": weekly_out,
        "tw_recap": tw_recap,
    }


def parse_origin_destination(value: str) -> Tuple[str, str]:
    if "->" in value:
        origin, destination = value.split("->", 1)
        return origin.strip(), destination.strip()
    return value.strip(), "-"


def compute_stock(item_index: Dict[str, ItemInfo], movement_data):
    stock_summary = []
    for item_name, info in item_index.items():
        inbound = movement_data["inbound"].get(item_name, Counter())
        outbound = movement_data["outbound"].get(item_name, Counter())
        total_in = sum(inbound.values())
        total_out = sum(outbound.values())
        final_qty = info.opening + total_in - total_out
        fisik = info.fisik
        system_qty = final_qty
        selisih = fisik - system_qty
        denom = fisik if fisik else system_qty if system_qty else 1
        persentase = abs(selisih) / denom if denom else 0
        stock_summary.append({
            "KODE": info.code,
            "ITEM": item_name,
            "STOCK_AWAL": info.opening,
            "MRD": inbound.get("MRD", 0),
            "ADJUST_IN": inbound.get("ADJUST_IN", 0),
            "TW_IN": inbound.get("TW_IN", 0),
            "FILLING": outbound.get("FILLING", 0),
            "ADJUST_OUT": outbound.get("ADJUST_OUT", 0),
            "TW_OUT": outbound.get("TW_OUT", 0),
            "STOCK_AKHIR": final_qty,
            "VENUS": system_qty,
            "FISIK": fisik,
            "SELISIH": selisih,
            "PERSENTASE": persentase,
            "QTY_PER_DUS": info.qty_per_dus,
            "KET": info.ket,
        })
    stock_summary.sort(key=lambda x: x["ITEM"])
    return stock_summary


def top_records(counter_map: Dict, limit: int = 10):
    records = []
    for key, counter in counter_map.items():
        for item, qty in counter.items():
            records.append((key, item, qty))
    records.sort(key=lambda x: x[2], reverse=True)
    return records[:limit]


def format_date_key(key):
    if isinstance(key, tuple) and len(key) == 2:
        year, week = key
        return f"{year}-W{week:02d}"
    if isinstance(key, date):
        return key.isoformat()
    return str(key)


def make_table(headers: List[str], rows: List[Iterable]) -> str:
    table = ["| " + " | ".join(headers) + " |"]
    table.append("|" + "|".join([" --- " for _ in headers]) + "|")
    for row in rows:
        table.append("| " + " | ".join(str(cell) for cell in row) + " |")
    return "\n".join(table)


def build_stock_table(stock_summary: List[dict]) -> str:
    headers = [
        "Kode",
        "Item",
        "Awal",
        "MRD",
        "Adj In",
        "TW In",
        "Filling",
        "Adj Out",
        "TW Out",
        "Akhir",
        "Fisik",
        "Selisih",
        "%",
        "Qty/Dus",
        "Ket",
    ]
    rows = []
    for row in stock_summary:
        rows.append([
            row["KODE"],
            row["ITEM"],
            row["STOCK_AWAL"],
            row["MRD"],
            row["ADJUST_IN"],
            row["TW_IN"],
            row["FILLING"],
            row["ADJUST_OUT"],
            row["TW_OUT"],
            row["STOCK_AKHIR"],
            row["FISIK"],
            row["SELISIH"],
            f"{row['PERSENTASE']*100:.2f}%",
            row["QTY_PER_DUS"],
            row["KET"],
        ])
    return make_table(headers, rows)


def build_top_table(records: List[Tuple], title_key: str) -> str:
    headers = [title_key, "Item", "Qty"]
    rows = []
    for key, item, qty in records:
        rows.append([format_date_key(key), item, qty])
    return make_table(headers, rows)


def build_selisih_table(stock_summary: List[dict], limit: int = 5) -> str:
    sorted_rows = sorted(stock_summary, key=lambda x: abs(x["SELISIH"]), reverse=True)[:limit]
    headers = ["Item", "Selisih", "%", "Ket", "Rekomendasi"]
    rows = []
    for row in sorted_rows:
        if row["SELISIH"] > 0:
            rekom = "Adjust In"
        elif row["SELISIH"] < 0:
            rekom = "Adjust Out"
        else:
            rekom = "Monitor"
        rows.append([
            row["ITEM"],
            row["SELISIH"],
            f"{row['PERSENTASE']*100:.2f}%",
            row["KET"],
            rekom,
        ])
    return make_table(headers, rows)


def build_tw_table(tw_recap: Dict[Tuple[str, str, str], Counter]) -> str:
    headers = ["Item", "Asal", "Tujuan", "Total Qty", "Frekuensi"]
    rows = []
    for (item, origin, destination), counter in sorted(tw_recap.items(), key=lambda x: (x[0][0], -x[1]["qty"])):
        rows.append([
            item,
            origin,
            destination,
            counter["qty"],
            counter["count"],
        ])
    return make_table(headers, rows)


def detect_anomalies(stock_summary: List[dict], movement_data, data):
    anomalies = []

    for row in stock_summary:
        if row["PERSENTASE"] > 0.05:
            anomalies.append(f"Persentase selisih {row['ITEM']} {row['PERSENTASE']*100:.1f}% melebihi batas 5%.")

    adjust_counts = Counter()
    for row in data.get("ADJUST IN", []):
        adjust_counts[row["NAMA BARANG"]] += 1
    for row in data.get("ADJUST OUT", []):
        adjust_counts[row["NAMA BARANG"]] += 1
    for item, count in adjust_counts.items():
        if count > 1:
            anomalies.append(f"{item} mengalami {count} kali penyesuaian dalam periode ini.")

    tw_recap = movement_data["tw_recap"]
    transfer_counts = Counter()
    for (item, origin, destination), counter in tw_recap.items():
        transfer_counts[item] += counter["count"]
    for item, count in transfer_counts.items():
        if count > 2:
            anomalies.append(f"{item} ditransfer {count} kali antar gudang, perlu cek kebutuhan routing.")

    return anomalies


def build_recommendations(stock_summary: List[dict], anomalies: List[str]) -> List[str]:
    recs = []
    for row in stock_summary:
        if abs(row["SELISIH"]) >= 50:
            if row["SELISIH"] > 0:
                recs.append(f"Segera buat adjust in {row['ITEM']} sejumlah {row['SELISIH']} untuk samakan fisik dan sistem.")
            else:
                recs.append(f"Lakukan stock count ulang dan ajukan adjust out {row['ITEM']} {abs(row['SELISIH'])} unit jika konfirmasi selisih.")
    if anomalies:
        recs.append("Review SOP label & pencatatan untuk item dengan anomali di atas, dan tetapkan jadwal pengecekan mingguan.")
    recs.append("Gunakan bundling qty per dus saat transfer untuk mengurangi selisih konversi.")
    return recs


def main():
    data_path = Path("data") / "inventory_packaging.json"
    data = load_data(data_path)
    item_index = build_item_index(data["STOCK"])
    movement_data = aggregate_movements(data, item_index)
    stock_summary = compute_stock(item_index, movement_data)

    daily_in_top = top_records(movement_data["daily_in"])
    daily_out_top = top_records(movement_data["daily_out"])
    weekly_in_top = top_records(movement_data["weekly_in"])
    weekly_out_top = top_records(movement_data["weekly_out"])

    stock_table = build_stock_table(stock_summary)
    daily_in_table = build_top_table(daily_in_top, "Tanggal")
    daily_out_table = build_top_table(daily_out_top, "Tanggal")
    weekly_in_table = build_top_table(weekly_in_top, "Minggu")
    weekly_out_table = build_top_table(weekly_out_top, "Minggu")
    selisih_table = build_selisih_table(stock_summary)
    tw_table = build_tw_table(movement_data["tw_recap"])
    anomalies = detect_anomalies(stock_summary, movement_data, data)
    recommendations = build_recommendations(stock_summary, anomalies)

    report_sections = [
        "# Laporan Inventory Packaging",
        "## Ringkasan Stok Akhir",
        stock_table,
        "\n## Top 10 Harian Barang Masuk",
        daily_in_table,
        "\n## Top 10 Harian Barang Keluar",
        daily_out_table,
        "\n## Top 10 Mingguan Barang Masuk",
        weekly_in_table,
        "\n## Top 10 Mingguan Barang Keluar",
        weekly_out_table,
        "\n## Selisih Terbesar & Rekomendasi",
        selisih_table,
        "\n## Rekap Transfer Warehouse",
        tw_table,
        "\n## Insight Anomali",
    ]
    if anomalies:
        report_sections.append("\n".join(f"- {item}" for item in anomalies))
    else:
        report_sections.append("- Tidak ada anomali signifikan terdeteksi.")

    report_sections.append("\n## Rekomendasi Proses")
    report_sections.append("\n".join(f"- {rec}" for rec in recommendations))

    report_text = "\n\n".join(report_sections) + "\n"

    output_path = Path("analysis") / "report.md"
    output_path.write_text(report_text, encoding="utf-8")

    print(report_text)


if __name__ == "__main__":
    main()
