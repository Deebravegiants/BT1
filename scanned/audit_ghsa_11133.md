# [H] Undertow is Vulnerable to HTTP Request/Response Smuggling

## Summary
Severity: High
Advisory: GHSA-3gv6-g396-9v4r
CVE: CVE-2026-28367
CWE: CWE-444
Ecosystem: Maven
CVSS: CVSS:3.1/AV:N/AC:H/PR:N/UI:N/S:C/C:H/I:H/A:N (CVSS_V3)
Published: 2026-03-27
Source: https://github.com/advisories/GHSA-3gv6-g396-9v4r
Type: github-advisory

## Affected
- Maven: `io.undertow:undertow-parent` — affected >=0

## Details
A flaw was found in Undertow. A remote attacker can exploit this vulnerability by sending `\r\r\r` as a header block terminator. This can be used for request smuggling with certain proxy servers, such as older versions of Apache Traffic Server and Google Cloud Classic Application Load Balancer, potentially leading to unauthorized access or manipulation of web requests.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2026-28367
- https://access.redhat.com/errata/RHSA-2026:25125
- https://access.redhat.com/errata/RHSA-2026:25126
- https://access.redhat.com/security/cve/CVE-2026-28367
- https://bugzilla.redhat.com/show_bug.cgi?id=2443260
- https://github.com/undertow-io/undertow
