# [H] Spring Data Commons contain a property path parser vulnerability caused by unlimited resource allocation

## Summary
Severity: High
Advisory: GHSA-5q8m-mqmx-pxp9
CVE: CVE-2018-1274
CWE: CWE-770
Ecosystem: Maven
CVSS: CVSS:3.0/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:H (CVSS_V3)
Published: 2018-10-17
Source: https://github.com/advisories/GHSA-5q8m-mqmx-pxp9
Type: github-advisory

## Affected
- Maven: `org.springframework.data:spring-data-commons` — affected >=0 <1.13.11
- Maven: `org.springframework.data:spring-data-commons` — affected >=2.0.0 <2.0.6

## Details
Spring Data Commons, versions 1.13 to 1.13.10, 2.0 to 2.0.5, and older unsupported versions, contain a property path parser vulnerability caused by unlimited resource allocation. An unauthenticated remote malicious user (or attacker) can issue requests against Spring Data REST endpoints or endpoints using property path parsing which can cause a denial of service (CPU and memory consumption).

## References
- https://nvd.nist.gov/vuln/detail/CVE-2018-1274
- https://github.com/spring-projects/spring-data-commons/commit/371f6590c509c72f8e600f3d05e110941607fba
- https://github.com/spring-projects/spring-data-commons/commit/3d8576fe4e4e71c23b9e6796b32fd56e51182ee
- https://github.com/advisories/GHSA-5q8m-mqmx-pxp9
- https://pivotal.io/security/cve-2018-1274
- https://www.oracle.com/security-alerts/cpujul2022.html
- http://www.securityfocus.com/bid/103769
