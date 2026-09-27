# [M] HTTP Request Smuggling Leading to Client Timeouts in resteasy-netty4

## Summary
Severity: Medium
Advisory: GHSA-5wpr-cj9p-959r
CVE: CVE-2024-9622
CWE: CWE-444
Ecosystem: Maven
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:L (CVSS_V3)
Published: 2024-10-08
Source: https://github.com/advisories/GHSA-5wpr-cj9p-959r
Type: github-advisory

## Affected
- Maven: `org.jboss.resteasy:resteasy-netty4-cdi` — affected >=0

## Details
A vulnerability was found in the resteasy-netty4 library arising from improper handling of HTTP requests using smuggling techniques. When an HTTP smuggling request with an ASCII control character is sent, it causes the Netty HttpObjectDecoder to transition into a BAD_MESSAGE state. As a result, any subsequent legitimate requests on the same connection are ignored, leading to client timeouts, which may impact systems using load balancers and expose them to risk.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2024-9622
- https://access.redhat.com/security/cve/CVE-2024-9622
- https://bugzilla.redhat.com/show_bug.cgi?id=2317179
- https://github.com/orgs/resteasy/discussions/4351
- https://github.com/resteasy/resteasy
