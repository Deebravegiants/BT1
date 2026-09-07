# [M] keycloak-core vulnerable to timing attacks against JWS token verification

## Summary
Severity: Medium
Advisory: GHSA-w6gv-3r3v-gwgj
CVE: CVE-2017-2585
CWE: CWE-200
Ecosystem: Maven
CVSS: CVSS:3.0/AV:N/AC:H/PR:N/UI:N/S:U/C:H/I:N/A:N (CVSS_V3)
Published: 2018-10-18
Source: https://github.com/advisories/GHSA-w6gv-3r3v-gwgj
Type: github-advisory

## Affected
- Maven: `org.keycloak:keycloak-core` — affected >=0 <2.5.1

## Details
Red Hat Keycloak before version 2.5.1 has an implementation of HMAC verification for JWS tokens that uses a method that runs in non-constant time, potentially leaving the application vulnerable to timing attacks.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2017-2585
- https://access.redhat.com/errata/RHSA-2017:0872
- https://access.redhat.com/errata/RHSA-2017:0873
- https://bugzilla.redhat.com/show_bug.cgi?id=1412376
- https://github.com/advisories/GHSA-w6gv-3r3v-gwgj
- https://web.archive.org/web/20170420113802/http://www.securitytracker.com/id/1038180
- https://web.archive.org/web/20200227175650/http://www.securityfocus.com/bid/97393
- http://rhn.redhat.com/errata/RHSA-2017-0876.html
