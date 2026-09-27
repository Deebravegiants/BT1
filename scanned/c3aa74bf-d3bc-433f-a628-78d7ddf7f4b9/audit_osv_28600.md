# [H] Apache Traffic Server: Invalid Accept-Encoding can force forwarding requests

## Summary
Severity: High
Advisory: CVE-2024-35296
CVSS: 8.2 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:H/A:L)
Published: 2024-07-26
Source: https://osv.dev/vulnerability/CVE-2024-35296
Type: osv

## Details
Invalid Accept-Encoding header can cause Apache Traffic Server to fail cache lookup and force forwarding requests.

This issue affects Apache Traffic Server: from 8.0.0 through 8.1.10, from 9.0.0 through 9.2.4.

Users are recommended to upgrade to version 8.1.11 or 9.2.5, which fixes the issue.

## References
- https://lists.debian.org/debian-lts-announce/2024/09/msg00040.html
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2024/35xxx/CVE-2024-35296.json
- https://lists.apache.org/thread/c4mcmpblgl8kkmyt56t23543gp8v56m0
- https://nvd.nist.gov/vuln/detail/CVE-2024-35296
