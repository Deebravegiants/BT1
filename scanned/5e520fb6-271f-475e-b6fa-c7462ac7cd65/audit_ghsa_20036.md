# [H] Quarkus CORS filter allows simple GET and POST requests with an invalid Origin to proceed

## Summary
Severity: High
Advisory: GHSA-9895-g6x5-xwcp
CVE: CVE-2022-4147
CWE: CWE-285
Ecosystem: Maven
CVSS: CVSS:3.1/AV:N/AC:H/PR:N/UI:R/S:U/C:H/I:H/A:H (CVSS_V3)
Published: 2022-12-06
Source: https://github.com/advisories/GHSA-9895-g6x5-xwcp
Type: github-advisory

## Affected
- Maven: `io.quarkus:quarkus-vertx-http` — affected >=2.14.0.CR1 <2.14.2.Final
- Maven: `io.quarkus:quarkus-vertx-http` — affected >=0 <2.13.5.Final

## Details
Quarkus CORS filter allows simple GET and POST requests with invalid Origin to proceed. Simple GET or POST requests made with XMLHttpRequest are the ones which have no event listeners registered on the object returned by the XMLHttpRequest upload property and have no ReadableStream object used in the request.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2022-4147
- https://access.redhat.com/security/cve/CVE-2022-4147
- https://bugzilla.redhat.com/show_bug.cgi?id=2148867
- https://github.com/quarkusio/quarkus
- https://quarkus.io/blog/quarkus-2-14-2-final-released
