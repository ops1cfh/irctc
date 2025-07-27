import fitz  # PyMuPDF
import streamlit as st
from pathlib import Path
import tempfile
import os

def extract_fare(text: str) -> float:
    for line in text.splitlines():
        if "Ticket Fare" in line:
            try:
                return float(line.split()[-1])
            except ValueError:
                continue
    raise ValueError("Ticket Fare not found.")

def extract_total_fare(text: str) -> float:
    for line in text.splitlines():
        if "Total Fare" in line:
            try:
                return float(line.split()[-1])
            except ValueError:
                continue
    raise ValueError("Total Fare not found.")

def update_irctc_ticket(input_pdf: Path, output_pdf: Path, logo_path: Path | None = None):
    doc = fitz.open(input_pdf)
    page = doc[0]
    text = page.get_text()

    ticket_fare = extract_fare(text)
    total_fare = extract_total_fare(text)
    pg_charge = round(ticket_fare * 0.02, 2)
    new_total = round(total_fare + pg_charge, 2)

    insert_y = None
    for block in page.get_text("dict")['blocks']:
        for line in block.get("lines", []):
            for span in line.get("spans", []):
                if "Travel Insurance Premium" in span["text"]:
                    insert_y = span["bbox"][1] + 15
                if "Total Fare" in span["text"]:
                    page.draw_line((span["bbox"][0], span["bbox"][1] + 5),
                                   (span["bbox"][2], span["bbox"][1] + 5),
                                   color=(1, 0, 0))

    if insert_y:
        page.insert_text((72, insert_y), f"PG Charges (2%): ₹ {pg_charge:.2f}", fontsize=9)
        page.insert_text((72, insert_y + 15), f"Updated Total Fare: ₹ {new_total:.2f}", fontsize=9, color=(0, 0, 1))

    if logo_path and logo_path.exists():
        img_rect = fitz.Rect(page.rect.width - 120, 20, page.rect.width - 20, 60)
        page.insert_image(img_rect, filename=str(logo_path))

    doc.save(output_pdf)
    doc.close()

# Replit auto run
os.system("streamlit run irctc_ticket_app.py")
