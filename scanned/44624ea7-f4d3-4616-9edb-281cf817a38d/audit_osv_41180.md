# [M] Apache Traffic Server: Remap configuration lifetime and TOCTOU errors cause use-after-free

## Summary
Severity: Medium
Advisory: CVE-2026-58164
CVSS: 6.0 (CVSS:4.0/AV:N/AC:L/AT:P/PR:N/UI:N/VC:L/VI:L/VA:H/SC:N/SI:N/SA:N)
Published: 2026-07-29
Source: https://osv.dev/vulnerability/CVE-2026-58164
Type: osv

## Details
Apache Traffic Server has use-after-free and time-of-check/time-of-use errors in remap configuration handling.

This issue affects Apache Traffic Server: from 8.0.0 through 8.1.9, from 9.0.0 through 9.2.14, from 10.0.0 through 10.1.3.

Users are recommended to upgrade to version 9.2.15 or 10.1.4, which fix the issue.

## References
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/58xxx/CVE-2026-58164.json
- https://lists.apache.org/thread/5prl9glcm9g2swnq9hqxvnokylm1gr6d
- https://nvd.nist.gov/vuln/detail/CVE-2026-58164
