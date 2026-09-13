# [C] A buffer overflow in rethinkdb/rethinkdb

## Summary
Severity: Critical
Advisory: CVE-2026-24810
CVSS: 9.0 (CVSS:4.0/AV:N/AC:L/AT:N/PR:N/UI:N/VC:H/VI:H/VA:H/SC:H/SI:H/SA:H/S:N/AU:Y/R:U/V:C/RE:M/U:Red)
Published: 2026-01-27
Source: https://osv.dev/vulnerability/CVE-2026-24810
Type: osv

## Details
Buffer Copy without Checking Size of Input ('Classic Buffer Overflow') vulnerability in rethinkdb (src/cjson modules). This vulnerability is associated with program files cJSON.Cc.

This issue affects rethinkdb: through v2.4.4.

## References
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/24xxx/CVE-2026-24810.json
- https://nvd.nist.gov/vuln/detail/CVE-2026-24810
- https://github.com/rethinkdb/rethinkdb/pull/7163
- https://github.com/rethinkdb/rethinkdb
