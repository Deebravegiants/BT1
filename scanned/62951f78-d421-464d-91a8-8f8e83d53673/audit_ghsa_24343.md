# [M] Improper Authentication in Jenkins Blue Ocean Plugin

## Summary
Severity: Medium
Advisory: GHSA-rm5m-9mx4-g5r7
CVE: CVE-2017-1000110
CWE: CWE-287
Ecosystem: Maven
CVSS: CVSS:3.0/AV:N/AC:L/PR:L/UI:N/S:U/C:N/I:L/A:N (CVSS_V3)
Published: 2022-05-13
Source: https://github.com/advisories/GHSA-rm5m-9mx4-g5r7
Type: github-advisory

## Affected
- Maven: `io.jenkins.blueocean:blueocean` — affected >=0 <1.2.0

## Details
Blue Ocean allows the creation of GitHub organization folders that are set up to scan a GitHub organization for repositories and branches containing a Jenkinsfile, and create corresponding pipelines in Jenkins. It did not properly check the current user's authentication and authorization when configuring existing GitHub organization folders. This allowed users with read access to the GitHub organization folder to reconfigure it, including changing the GitHub API endpoint for the organization folder to an attacker-controlled server to obtain the GitHub access token, if the organization folder was initially created using Blue Ocean.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2017-1000110
- https://jenkins.io/security/advisory/2017-08-07
