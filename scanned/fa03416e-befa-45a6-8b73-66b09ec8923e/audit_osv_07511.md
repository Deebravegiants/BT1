# [H] BIT-sqlite-2026-51296

## Summary
Severity: High
Advisory: BIT-sqlite-2026-51296
Aliases: CVE-2026-51296
Ecosystem: Bitnami
Published: 2026-07-30
Source: https://osv.dev/vulnerability/BIT-sqlite-2026-51296
Type: osv

## Affected
- Bitnami: `sqlite` — affected >=3.41.0

## Details
SQLite 3.41 has a use-after-free vulnerability in jsonRemoveFunc of SQLite JSON module. The parsed JSON object is freed at line 3555, while line 3575 still calls jsonLookupStep with the released pointer. Remote attackers can exploit this flaw to crash the service and leak heap memory information.

## References
- https://github.com/programmervuln/cveadvisory-/commit/75a435c839a4bcc6ca2ad21e3b07c978d814acb2
- https://github.com/sqlite/sqlite/blob/master/src/json.c
- https://nvd.nist.gov/vuln/detail/CVE-2026-51296
