# [M] Moderate severity vulnerability that affects io.vertx:vertx-core

## Summary
Severity: Medium
Advisory: GHSA-6cw8-7j6c-hccp
CVE: CVE-2018-12537
CWE: CWE-93
Ecosystem: Maven
Published: 2018-10-19
Source: https://github.com/advisories/GHSA-6cw8-7j6c-hccp
Type: github-advisory

## Affected
- Maven: `io.vertx:vertx-core` — affected >=3.0.0 <3.5.2

## Details
In Eclipse Vert.x version 3.0 to 3.5.1, the HttpServer response headers and HttpClient request headers do not filter carriage return and line feed characters from the header value. This allow unfiltered values to inject a new header in the client request or server response.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2018-12537
- https://github.com/eclipse/vert.x/issues/2470
- https://github.com/eclipse/vert.x/commit/1bb6445226c39a95e7d07ce3caaf56828e8aab72
- https://access.redhat.com/errata/RHSA-2018:2371
- https://access.redhat.com/errata/RHSA-2018:3768
- https://bugs.eclipse.org/bugs/show_bug.cgi?id=536038
- https://bugzilla.redhat.com/show_bug.cgi?id=1591072
- https://github.com/advisories/GHSA-6cw8-7j6c-hccp
- https://www.compass-security.com/fileadmin/Datein/Research/Advisories/CSNC-2018-021_vertx.txt
