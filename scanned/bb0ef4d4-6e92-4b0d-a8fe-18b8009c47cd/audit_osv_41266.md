# [C] Apache CloudStack: Server-Side Request Forgery (SSRF) vulnerability in webhook module

## Summary
Severity: Critical
Advisory: CVE-2026-59085
CVSS: 9.1 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:N)
Published: 2026-08-21
Source: https://osv.dev/vulnerability/CVE-2026-59085
Type: osv

## Details
Server-Side Request Forgery (SSRF) vulnerability in Apache CloudStack's webhook module, exploitable via webhook delivery requests.

This issue affects Apache CloudStack: from 4.20.0.0 through 4.20.3.0 and from 4.21.0.0 through 4.22.1.0.

Users are recommended to upgrade to version 4.20.3.1 or 4.22.1.1 or later, which fixes the issue.

## References
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/59xxx/CVE-2026-59085.json
- https://lists.apache.org/thread/g6cwddtjrwbh1d56wjz4cfp3fzfm4kbc
- https://nvd.nist.gov/vuln/detail/CVE-2026-59085
