# [H] Apache Traffic Server: Incomplete field name check allows request smuggling

## Summary
Severity: High
Advisory: CVE-2023-38522
CVSS: 7.5 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:H/A:N)
Published: 2024-07-26
Source: https://osv.dev/vulnerability/CVE-2023-38522
Type: osv

## Details
Apache Traffic Server accepts characters that are not allowed for HTTP field names and forwards malformed requests to origin servers. This can be utilized for request smuggling and may also lead cache poisoning if the origin servers are vulnerable.

This issue affects Apache Traffic Server: from 8.0.0 through 8.1.10, from 9.0.0 through 9.2.4.

Users are recommended to upgrade to version 8.1.11 or 9.2.5, which fixes the issue.

## References
- https://lists.debian.org/debian-lts-announce/2024/09/msg00040.html
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2023/38xxx/CVE-2023-38522.json
- https://lists.apache.org/thread/c4mcmpblgl8kkmyt56t23543gp8v56m0
- https://nvd.nist.gov/vuln/detail/CVE-2023-38522
