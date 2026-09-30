# [C] Insecure cookie sharing in Hawtio

## Summary
Severity: Critical
Advisory: GHSA-m4j5-hgqq-5jf2
CVE: CVE-2017-2589
CWE: CWE-200
Ecosystem: Maven
CVSS: CVSS:3.0/AV:N/AC:L/PR:L/UI:R/S:C/C:H/I:H/A:H (CVSS_V3)
Published: 2022-05-13
Source: https://github.com/advisories/GHSA-m4j5-hgqq-5jf2
Type: github-advisory

## Affected
- Maven: `io.hawt:project` — affected >=0 <1.5.0

## Details
It was discovered that the hawtio servlet 1.4 uses a single HttpClient instance to proxy requests with a persistent cookie store (cookies are stored locally and are not passed between the client and the end URL) which means all clients using that proxy are sharing the same cookies.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2017-2589
- https://access.redhat.com/errata/RHSA-2017:1832
- https://bugzilla.redhat.com/show_bug.cgi?id=CVE-2017-2589
- https://github.com/hawtio/hawtio
- https://tadayoshi-sato.medium.com/securing-hawtio-f5fbfd5afcf0
