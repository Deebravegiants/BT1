# [M] Apache CXF: WS JSON request filter trusts metadata from an unvalidated first signature entry

## Summary
Severity: Medium
Advisory: GHSA-33j8-j763-4fv5
CVE: CVE-2026-50634
CWE: CWE-347
Ecosystem: Maven
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:L/I:L/A:N (CVSS_V3)
Published: 2026-06-12
Source: https://github.com/advisories/GHSA-33j8-j763-4fv5
Type: github-advisory

## Affected
- Maven: `org.apache.cxf:cxf-rt-rs-security-jose-jaxrs` — affected >=4.2.0 <4.2.2
- Maven: `org.apache.cxf:cxf-rt-rs-security-jose-jaxrs` — affected >=0 <4.1.7

## Details
A vulnerability in Apache CXF's JwsJsonContainerRequestFilter can be exploited to cause CXF to process metadata that was not authenticated by the accepted signature. This can bypass the application's assumption

that accepted `Content-Type` or protected HTTP-header metadata came from a verified signature entry, and may steer downstream JAX-RS entity parsing or signed-header consistency checks. Users are recommended to upgrade to versions 4.2.2 or 4.1.7, which fix this issue.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2026-50634
- https://github.com/apache/cxf
- https://lists.apache.org/thread/9nfwh9d3m4kznxrk1mz98hl0jml18k0p
- http://www.openwall.com/lists/oss-security/2026/06/11/11
