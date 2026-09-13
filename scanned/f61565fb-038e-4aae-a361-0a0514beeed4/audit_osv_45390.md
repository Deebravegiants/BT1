# [C] JLSEC-2026-1113

## Summary
Severity: Critical
Advisory: JLSEC-2026-1113
Ecosystem: Julia
CVSS: 9.8 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H)
Published: 2026-08-03
Source: https://osv.dev/vulnerability/JLSEC-2026-1113
Type: osv

## Affected
- Julia: `LibRaw_jll` — affected >=0.22.1+0 <0.22.2+0

## Details
An integer overflow vulnerability exists in the `deflate_dng_load_raw` functionality of LibRaw Commit 8dc68e2. A specially crafted malicious file can lead to a heap buffer overflow. An attacker can provide a malicious file to trigger this vulnerability.

## References
- https://talosintelligence.com/vulnerability_reports/TALOS-2026-2364
- https://www.talosintelligence.com/vulnerability_reports/TALOS-2026-2364
