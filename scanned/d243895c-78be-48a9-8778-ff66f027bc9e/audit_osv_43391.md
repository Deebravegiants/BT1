# [H] Apache Struts: Unbounded read of a Content Security Policy violation report

## Summary
Severity: High
Advisory: CVE-2026-73634
CVSS: 7.5 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:H)
Published: 2026-08-15
Source: https://osv.dev/vulnerability/CVE-2026-73634
Type: osv

## Details
Uncontrolled resource consumption vulnerability in Apache Struts. An application that exposes an endpoint collecting Content Security Policy violation reports reads the submitted report into memory without bounding how much it will accept, so a single request can exhaust the heap and deny service to other users. Such endpoints are ordinarily reachable without authentication. The core distribution maps no such endpoint by default; applications that do not collect violation reports are not affected.

This issue affects Apache Struts: from 6.0.0 through 6.10.0, from 7.0.0 through 7.2.1.

Users are recommended to upgrade to version 6.11.0 or 7.3.0, which fixes the issue.

## References
- https://cwiki.apache.org/confluence/display/WW/S2-073
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/73xxx/CVE-2026-73634.json
- https://nvd.nist.gov/vuln/detail/CVE-2026-73634
