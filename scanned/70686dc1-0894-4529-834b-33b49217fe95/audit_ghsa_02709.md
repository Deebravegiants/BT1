# [H] HTTP header injection in Sonatype Nexus Repository

## Summary
Severity: High
Advisory: GHSA-f34x-8pf6-qc9c
CVE: CVE-2021-40143
CWE: CWE-74
Ecosystem: Maven
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:L/A:N (CVSS_V3)
Published: 2021-09-08
Source: https://github.com/advisories/GHSA-f34x-8pf6-qc9c
Type: github-advisory

## Affected
- Maven: `org.sonatype.nexus:nexus-repository` — affected >=3.0.0 <3.34.0-01

## Details
Sonatype Nexus Repository 3.x through 3.33.1-01 is vulnerable to an HTTP header injection. By sending a crafted HTTP request, a remote attacker may disclose sensitive information or request external resources from a vulnerable instance.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2021-40143
- https://github.com/sonatype/nexus-public
- https://help.sonatype.com/repomanager3/release-notes/2021-release-notes
- https://issues.sonatype.org/secure/ReleaseNote.jspa
- https://support.sonatype.com/hc/en-us/articles/4405941762579
