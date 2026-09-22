# [M] Vert.x Web static handler component cache can be manipulated to deny the access to static files

## Summary
Severity: Medium
Advisory: GHSA-cphf-4846-3xx9
CVE: CVE-2026-1002
CWE: CWE-444
Ecosystem: Maven
CVSS: CVSS:4.0/AV:N/AC:L/AT:N/PR:N/UI:N/VC:N/VI:N/VA:L/SC:N/SI:N/SA:L (CVSS_V4)
Published: 2026-01-15
Source: https://github.com/advisories/GHSA-cphf-4846-3xx9
Type: github-advisory

## Affected
- Maven: `io.vertx:vertx-core` — affected >=0 <4.5.24
- Maven: `io.vertx:vertx-core` — affected >=5.0.0.CR1 <5.0.7

## Details
The Vert.x Web static handler component cache can be manipulated to deny the access to static files served by the handler using specifically crafted request URI.


The issue comes from an improper implementation of the C. rule of section 5.2.4 of RFC3986 and is fixed in Vert.x Core component (used by Vert.x Web):  https://github.com/eclipse-vertx/vert.x/pull/5895 



Steps to reproduce
Given a file served by the static handler, craft an URI that introduces a string like bar%2F..%2F after the last / char to deny the access to the URI with an HTTP 404 response. For example https://example.com/foo/index.html can be denied with https://example.com/foo/bar%2F..%2Findex.html

Mitgation
Disabling Static Handler cache fixes the issue.



StaticHandler staticHandler = StaticHandler.create().setCachingEnabled(false);

## References
- https://nvd.nist.gov/vuln/detail/CVE-2026-1002
- https://github.com/vert-x3/vertx-web/issues/2836
- https://github.com/eclipse-vertx/vert.x/pull/5894
- https://github.com/eclipse-vertx/vert.x/pull/5895
- https://github.com/eclipse-vertx/vert.x/commit/5b67f5d17788b2483d277c760f3f8154f9b2fed0
- https://github.com/eclipse-vertx/vert.x/commit/d007e7b418543eb1567fe95cf20f5450a5c2d047
- https://github.com/eclipse-vertx/vert.x
