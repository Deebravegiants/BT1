# [M] Apache Struts: Shared parsing state in the JSON plugin

## Summary
Severity: Medium
Advisory: CVE-2026-73631
CVSS: 4.3 (CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:L/I:N/A:N)
Published: 2026-08-15
Source: https://osv.dev/vulnerability/CVE-2026-73631
Type: osv

## Details
Exposure of data element to wrong session vulnerability in the JSON plugin of Apache Struts. Per-request parsing state could be shared across concurrent requests, allowing data associated with one request to become observable in another, and configured parsing limits not to be enforced as intended. Populating actions from a JSON request body is not enabled by default; applications that do not use the JSON plugin are not affected.

This issue affects Apache Struts: 7.2.1.

Users are recommended to upgrade to version 7.3.0, which fixes the issue.

## References
- https://cwiki.apache.org/confluence/display/WW/S2-070
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/73xxx/CVE-2026-73631.json
- https://nvd.nist.gov/vuln/detail/CVE-2026-73631
