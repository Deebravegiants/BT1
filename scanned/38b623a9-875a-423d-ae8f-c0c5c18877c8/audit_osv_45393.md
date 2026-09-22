# [C] An integer overflow vulnerability exists in the uncompressed_fp_dng_load_raw functionality of...

## Summary
Severity: Critical
Advisory: JLSEC-2026-1116
Ecosystem: Julia
CVSS: 9.8 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H)
Published: 2026-08-03
Source: https://osv.dev/vulnerability/JLSEC-2026-1116
Type: osv

## Affected
- Julia: `LibRaw_jll` — affected >=0.22.1+0 <0.22.2+0

## Details
An integer overflow vulnerability exists in the `uncompressed_fp_dng_load_raw` functionality of LibRaw Commit 8dc68e2. A specially crafted malicious file can lead to a heap buffer overflow. An attacker can provide a malicious file to trigger this vulnerability.

## References
- https://github.com/advisories/GHSA-rhmw-w7w3-c647
- https://nvd.nist.gov/vuln/detail/CVE-2026-24450
- https://talosintelligence.com/vulnerability_reports/TALOS-2026-2363
- https://www.talosintelligence.com/vulnerability_reports/TALOS-2026-2363
