# [H] Apache Traffic Server: Malformed chunked message body allows request smuggling

## Summary
Severity: High
Advisory: CVE-2024-53868
CVSS: 7.5 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:H/A:N)
Published: 2025-04-03
Source: https://osv.dev/vulnerability/CVE-2024-53868
Type: osv

## Details
Apache Traffic Server allows request smuggling if chunked messages are malformed. 





This issue affects Apache Traffic Server: from 9.2.0 through 9.2.9, from 10.0.0 through 10.0.4.

Users are recommended to upgrade to version 9.2.10 or 10.0.5, which fixes the issue.

## References
- http://www.openwall.com/lists/oss-security/2025/04/02/4
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2024/53xxx/CVE-2024-53868.json
- https://lists.apache.org/thread/rwyx91rsrnmpjbm04footfjjf6m9d1c9
- https://nvd.nist.gov/vuln/detail/CVE-2024-53868
