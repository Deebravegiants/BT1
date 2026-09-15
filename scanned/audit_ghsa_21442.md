# [M] Missing permission check in Jenkins Delete log Plugin

## Summary
Severity: Medium
Advisory: GHSA-j874-47xx-9xfg
CVE: CVE-2022-45394
CWE: CWE-862
Ecosystem: Maven
CVSS: CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:N/I:L/A:N (CVSS_V3)
Published: 2022-11-16
Source: https://github.com/advisories/GHSA-j874-47xx-9xfg
Type: github-advisory

## Affected
- Maven: `org.jenkins-ci.plugins:delete-log-plugin` — affected >=0

## Details
A missing permission check in Jenkins Delete log Plugin 1.0 and earlier allows attackers with Item/Read permission to delete build logs. As of publication of this advisory, there is no fix.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2022-45394
- https://github.com/jenkinsci/delete-log-plugin
- https://www.jenkins.io/security/advisory/2022-11-15/#SECURITY-2920
- http://www.openwall.com/lists/oss-security/2022/11/15/4
