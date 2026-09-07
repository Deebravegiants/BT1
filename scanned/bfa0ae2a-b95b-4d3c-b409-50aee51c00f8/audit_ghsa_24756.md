# [H] Jenkins StarTeam Plugin stores credentials in plain text 

## Summary
Severity: High
Advisory: GHSA-gvhp-v4m2-3rwf
CVE: CVE-2019-10277
CWE: CWE-522
Ecosystem: Maven
CVSS: CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H (CVSS_V3)
Published: 2022-05-13
Source: https://github.com/advisories/GHSA-gvhp-v4m2-3rwf
Type: github-advisory

## Affected
- Maven: `hudson.plugins:starteam` — affected >=0

## Details
Jenkins StarTeam Plugin stores credentials unencrypted in job config.xml files on the Jenkins master where they can be viewed by users with Extended Read permission, or access to the master file system.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2019-10277
- https://jenkins.io/security/advisory/2019-04-03/#SECURITY-1085
- http://www.openwall.com/lists/oss-security/2019/04/12/2
- http://www.securityfocus.com/bid/107790
