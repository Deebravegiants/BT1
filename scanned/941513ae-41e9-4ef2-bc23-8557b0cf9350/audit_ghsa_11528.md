# [M] Undertow: Denial of Service via Multipart/Form-Data Parsing on HTTP GET Requests

## Summary
Severity: Medium
Advisory: GHSA-3x3v-w654-m28m
CVE: CVE-2026-3260
CWE: CWE-770
Ecosystem: Maven
CVSS: CVSS:3.1/AV:N/AC:H/PR:N/UI:N/S:U/C:N/I:N/A:H (CVSS_V3)
Published: 2026-03-24
Source: https://github.com/advisories/GHSA-3x3v-w654-m28m
Type: github-advisory

## Affected
- Maven: `io.undertow:undertow-core` — affected >=0

## Details
A flaw was found in Undertow. A remote attacker could exploit this vulnerability by sending an HTTP GET request containing multipart/form-data content. If the underlying application processes parameters using methods like `getParameterMap()`, the server prematurely parses and stores this content to disk. This could lead to resource exhaustion, potentially resulting in a Denial of Service (DoS).

## References
- https://nvd.nist.gov/vuln/detail/CVE-2026-3260
- https://access.redhat.com/security/cve/CVE-2026-3260
- https://bugzilla.redhat.com/show_bug.cgi?id=2443010
- https://github.com/undertow-io/undertow
