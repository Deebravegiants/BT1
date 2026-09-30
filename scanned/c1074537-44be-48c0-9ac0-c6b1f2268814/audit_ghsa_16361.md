# [M] Micronaut management endpoints vulnerable to drive-by localhost attack

## Summary
Severity: Medium
Advisory: GHSA-583g-g682-crxf
CVE: CVE-2024-23639
CWE: CWE-15, CWE-610, CWE-664
Ecosystem: Maven
CVSS: CVSS:3.1/AV:L/AC:L/PR:N/UI:N/S:U/C:N/I:L/A:L (CVSS_V3)
Published: 2024-02-09
Source: https://github.com/advisories/GHSA-583g-g682-crxf
Type: github-advisory

## Affected
- Maven: `io.micronaut:micronaut-http-server` — affected >=0 <3.8.3
- Maven: `io.micronaut:micronaut-http-server-netty` — affected >=0 <3.8.3
- Maven: `io.micronaut:micronaut-http-server-tck` — affected >=0 <3.8.3

## Details
### Summary
Enabled but unsecured management endpoints are susceptible to drive-by localhost attacks. While not typical of a production application, these attacks may have more impact on a development environment where such endpoints may be flipped on without much thought.

### Details
A malicious/compromised website can make HTTP requests to `localhost`. Normally, such requests would trigger a CORS preflight check which would prevent the request; however, some requests are ["simple"](https://developer.mozilla.org/en-US/docs/Web/HTTP/CORS#simple_requests) and do not require a preflight check. These endpoints, if enabled and not secured, are vulnerable to being triggered.

### Impact
Production environments typically disable unused endpoints and secure/restrict access to needed endpoints. A more likely victim is the developer in their local development host, who has enabled endpoints without security for the sake of easing development.

## References
- https://github.com/micronaut-projects/micronaut-core/security/advisories/GHSA-583g-g682-crxf
- https://nvd.nist.gov/vuln/detail/CVE-2024-23639
- https://github.com/micronaut-projects/micronaut-core/pull/8642
- https://github.com/micronaut-projects/micronaut-core/commit/01adb21e57137caaf7004313d2055c5a78b1f47b
- https://developer.mozilla.org/en-US/docs/Web/HTTP/CORS#simple_requests
- https://github.com/micronaut-projects/micronaut-core
