# [M] Turso through 0.8.0-pre.8 Out-of-Bounds Read Denial of Service

## Summary
Severity: Medium
Advisory: CVE-2026-85698
CVSS: 6.0 (CVSS:4.0/AV:L/AC:L/AT:N/PR:N/UI:P/VC:N/VI:N/VA:H/SC:N/SI:N/SA:N)
Published: 2026-09-04
Source: https://osv.dev/vulnerability/CVE-2026-85698
Type: osv

## Details
Turso through 0.8.0-pre.8 contains an out-of-bounds read vulnerability in the table-leaf page reader that uses an attacker-controlled cell-count field without bounds validation. Attackers can craft a malicious database file with a modified cell count value to trigger an index-out-of-bounds panic when querying, causing denial of service in any application that opens untrusted database files.

## References
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/85xxx/CVE-2026-85698.json
- https://nvd.nist.gov/vuln/detail/CVE-2026-85698
- https://www.vulncheck.com/advisories/turso-through-0.8.0-pre.8-out-of-bounds-read-denial-of-service
- https://github.com/tursodatabase/turso/issues/7473
- https://github.com/tursodatabase/turso
- https://github.com/tursodatabase/turso/blob/v0.8.0-pre.8/core/storage/pager.rs
