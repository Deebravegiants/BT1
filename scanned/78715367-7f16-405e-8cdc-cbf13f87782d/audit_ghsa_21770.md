# [H] Keycloak Gatekeeper vulnerable to bypass on using lower case HTTP headers

## Summary
Severity: High
Advisory: GHSA-jh6m-3pqw-242h
CVE: CVE-2020-14359
CWE: CWE-305
Ecosystem: Go
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:L/I:L/A:L (CVSS_V3)
Published: 2022-02-09
Source: https://github.com/advisories/GHSA-jh6m-3pqw-242h
Type: github-advisory

## Affected
- Go: `github.com/keycloak/keycloak-gatekeeper` — affected >=0

## Details
A vulnerability was found in all versions of the deprecated package Keycloak Gatekeeper, where on using lower case HTTP headers (via cURL) we can bypass our Gatekeeper. Lower case headers are also accepted by some webservers (e.g. Jetty). This means there is no protection when we put a Gatekeeper in front of a Jetty server and use lowercase headers.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2020-14359
- https://github.com/keycloak/keycloak/issues/12934
- https://bugzilla.redhat.com/show_bug.cgi?id=1868591
- https://github.com/keycloak/keycloak-gatekeeper
- https://issues.jboss.org/browse/KEYCLOAK-14090
- https://web.archive.org/web/20190613000352/github.com/keycloak/keycloak-gatekeeper
