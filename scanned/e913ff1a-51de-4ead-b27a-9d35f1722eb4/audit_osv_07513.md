# [M] BIT-sqlite-2026-51298

## Summary
Severity: Medium
Advisory: BIT-sqlite-2026-51298
Aliases: CVE-2026-51298
Ecosystem: Bitnami
Published: 2026-07-30
Source: https://osv.dev/vulnerability/BIT-sqlite-2026-51298
Type: osv

## Affected
- Bitnami: `sqlite` — affected >=3.41.0

## Details
sqlite 3.41 is vulnerable to use after free in the JSON extraction function. After releasing JsonParse object memory via jsonParseFree(), the program still accesses internal member of the freed pointer, which can cause service crash and denial of service.

## References
- https://github.com/programmervuln/cveadvisory-/blob/main/CVE-2026-51298
- https://github.com/sqlite/sqlite/blob/master/src/json.c
- https://nvd.nist.gov/vuln/detail/CVE-2026-51298
