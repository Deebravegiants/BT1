# [C] Hudson XML API susceptible to External Entity Injection Vunerability prior to v3.3.2

## Summary
Severity: Critical
Advisory: GHSA-j3h2-8mf8-j5r2
CVE: CVE-2015-8031
CWE: CWE-611
Ecosystem: Maven
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H (CVSS_V3)
Published: 2022-07-15
Source: https://github.com/advisories/GHSA-j3h2-8mf8-j5r2
Type: github-advisory

## Affected
- Maven: `org.jvnet.hudson.main:hudson-core` — affected >=0 <3.3.2

## Details
In versions prior to 3.3.2, Hudson exhibits a flaw in its XML API processing that can allow access to potentially sensitive information on the filesystem of the Hudson master server.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2015-8031
- https://github.com/advisories/GHSA-j3h2-8mf8-j5r2
- https://github.com/hudson/hudson-2.x
- https://security.snyk.io/vuln/SNYK-JAVA-ORGJVNETHUDSONMAIN-31221
- https://wiki.eclipse.org/Hudson-ci/alerts/CVE-2015-8031
