# [M] Jenkins Fogbugz Plugin has missing permissions check

## Summary
Severity: Medium
Advisory: GHSA-2482-gr3v-f3f3
CVE: CVE-2023-30522
CWE: CWE-862
Ecosystem: Maven
CVSS: CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:N/I:L/A:N (CVSS_V3)
Published: 2023-04-12
Source: https://github.com/advisories/GHSA-2482-gr3v-f3f3
Type: github-advisory

## Affected
- Maven: `org.jenkins-ci.plugins:fogbugz` — affected >=0

## Details
Jenkins Fogbugz Plugin provides a webhook endpoint at `/fbTrigger/` that can be used to trigger builds of any jobs.

In Fogbugz Plugin 2.2.17 and earlier, this endpoint can be accessed by attackers with Item/Read permission, allowing them to trigger builds of jobs specified in a `jobname` request parameter.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2023-30522
- https://www.jenkins.io/security/advisory/2023-04-12/#SECURITY-2873
- http://www.openwall.com/lists/oss-security/2023/04/13/3
