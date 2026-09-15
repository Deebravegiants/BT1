# [H] Apache Traffic Server: Certifier plugin trusts client SNI when generating certificates

## Summary
Severity: High
Advisory: CVE-2026-58162
CVSS: 7.5 (CVSS:4.0/AV:N/AC:L/AT:P/PR:N/UI:N/VC:L/VI:H/VA:H/SC:N/SI:N/SA:N)
Published: 2026-07-29
Source: https://osv.dev/vulnerability/CVE-2026-58162
Type: osv

## Details
The Apache Traffic Server certifier plugin generates certificates based on attacker-controlled client SNI.

This issue affects Apache Traffic Server: from 8.0.0 through 8.1.9, from 9.0.0 through 9.2.14, from 10.0.0 through 10.1.3.

Users are recommended to upgrade to version 9.2.15 or 10.1.4, which fix the issue.

## References
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/58xxx/CVE-2026-58162.json
- https://lists.apache.org/thread/5prl9glcm9g2swnq9hqxvnokylm1gr6d
- https://nvd.nist.gov/vuln/detail/CVE-2026-58162
