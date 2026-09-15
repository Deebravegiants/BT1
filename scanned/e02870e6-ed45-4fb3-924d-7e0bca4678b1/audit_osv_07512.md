# [H] BIT-sqlite-2026-51297

## Summary
Severity: High
Advisory: BIT-sqlite-2026-51297
Aliases: CVE-2026-51297
Ecosystem: Bitnami
Published: 2026-07-30
Source: https://osv.dev/vulnerability/BIT-sqlite-2026-51297
Type: osv

## Affected
- Bitnami: `sqlite` — affected >=3.41.0

## Details
sqlite 3.41 has a use-after-free vulnerability in the JSON parsing logic. Remote adversaries can craft malicious JSON payload to trigger memory free followed by illegal memory access, which may lead to arbitrary code execution, sensitive information leakage and service denial.

## References
- https://github.com/programmervuln/cveadvisory-/blob/main/CVE-2026-51297
- https://github.com/sqlite/sqlite/blob/master/src/json.c
- https://nvd.nist.gov/vuln/detail/CVE-2026-51297
