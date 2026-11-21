# Build notes — Republic of Ostravia passport spread

## The country

- **Republic of Ostravia** (Ostravian: *Republika Ostravija*), capital
  **Veligrad**. A landlocked country whose borders are crossed by rail and
  road — which is why its neighbour's visa is valid "by road or rail only".
- Code **OVR**, currency the **koruna (OK)**.
- Neighbours: **Kharadia** (south, crossed at Meran Bridge / Veligrad Rail)
  and **Luthenia** (west, crossed at the shared Vess Junction rail post).

## The holder and document

| Field | Value |
|---|---|
| Surname / Given names | MERAVIK, Ilona |
| Nationality | Ostravian |
| Date of birth | 14 MAR 1989, Veligrad |
| Sex | F |
| Type / Code | P / OVR |
| Passport No | OV4182073 |
| Issued | 03 JUN 2021 |
| Expires | 03 JUN 2031 |
| Authority | Ministry of the Interior — Veligrad |

## Date-consistency table (nothing predates issue, nothing is in the future)

| Date | Event |
|---|---|
| 03 JUN 2021 | Passport issued (all travel below is after this) |
| 28 SEP 2022 | Kharadia visa issued at Veligrad; fee stamp "FEE PAID — 40 OK" same date |
| 14 OCT 2022 | Exit Ostravia (Veligrad Rail) → Entry Kharadia (Meran Bridge) |
| 21 OCT 2022 | Exit Kharadia (Meran Bridge) → Entry Ostravia (Veligrad Rail) |
| 09 MAY 2024 | Exit Ostravia (Vess Junction) → Entry Luthenia (Vess Junction) |
| 16 MAY 2024 | Exit Luthenia (Vess Junction) → Entry Ostravia (Vess Junction) |
| 05 SEP 2025 | Exit Ostravia (Veligrad Rail) → Entry Kharadia (Meran Bridge) |
| 12 SEP 2025 | Exit Kharadia (Meran Bridge) → Entry Ostravia (Veligrad Rail) |
| 03 JUN 2031 | Passport expiry |

The stamp dates are `datetime.date` values in the code; an assertion in
`main.py` checks every stamp falls after the issue date and not after
21 NOV 2026, and the visa issue date sits between issue and first trip.

## Machine-readable zone

Two 44-character ICAO TD3 lines. All five check digits (document number,
date of birth, expiry, personal number, composite) are computed with the
7-3-1 weighting in code and were verified against an independent
implementation:

```
P<OVRMERAVIK<<ILONA<<<<<<<<<<<<<<<<<<<<<<<<<
OV41820732OVR8903141F3106039<<<<<<<<<<<<<<04
```

## Design choices

- One serif (headers), one sans (fields and stamps), one monospace (MRZ) —
  the DejaVu family — at consistent sizes, with shared margins and rules
  so both pages read as one printed document.
- Cream security paper with a very light sine-line guilloche, a microprint
  border repeating the country name, and gutter shading at the centre
  seam. Restrained on purpose: a passport is a working document.
- The portrait (a supplied ID photo, `portrait.jpg`) appears at full size
  with a thin border and again as a small faded ghost copy, as on real
  data pages. The holder's signature is drawn as an ink squiggle.
- Stamps are drawn as separate ink layers (blue Ostravia rectangles, red
  Kharadia rounded rectangles, black Luthenia ovals), slightly rotated and
  softened, in faded ink. The Kharadian visa is a sticker in a slightly
  different paper tone; the round purple fee stamp overlaps its corner.

## Verification

- Two runs of `main.py` produce byte-identical output.
- Output: PNG, 1024×768, 322,180 bytes (limit 1,048,576). If a PNG ever
  exceeded the limit the program falls back to JPEG bytes at the same
  path, which the gate also accepts.
- A revision pass after visual review removed a header/code collision,
  dropped a non-standard caption under the MRZ, lightened the guilloche,
  and gave the stamps and signature a less mechanical feel.
