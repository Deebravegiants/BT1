# [H] Incorrect Resource Transfer Between Spheres in Grails

## Summary
Severity: High
Advisory: GHSA-pmxf-4v8c-rwr7
CVE: CVE-2019-12728
CWE: CWE-494, CWE-669
Ecosystem: Maven
CVSS: CVSS:3.1/AV:N/AC:H/PR:N/UI:N/S:U/C:H/I:H/A:H (CVSS_V3)
Published: 2022-05-24
Source: https://github.com/advisories/GHSA-pmxf-4v8c-rwr7
Type: github-advisory

## Affected
- Maven: `org.grails:grails-core` — affected >=0 <3.3.10

## Details
Grails before 3.3.10 used cleartext HTTP to resolve the SDKMan notification service. NOTE: users' apps were not resolving dependencies over cleartext HTTP.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2019-12728
- https://github.com/grails/grails-core/issues/11250
- https://objectcomputing.com/news/2019/05/30/possible-grails-mitm-vulnerability
