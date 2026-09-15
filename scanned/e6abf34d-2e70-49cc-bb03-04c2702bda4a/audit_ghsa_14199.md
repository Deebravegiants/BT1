# [M] Lack of authentication mechanism in Jenkins TurboScript Plugin webhook

## Summary
Severity: Medium
Advisory: GHSA-7gqc-q9mc-6348
CVE: CVE-2023-30532
CWE: CWE-862
Ecosystem: Maven
CVSS: CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:N/I:H/A:N (CVSS_V3)
Published: 2023-04-12
Source: https://github.com/advisories/GHSA-7gqc-q9mc-6348
Type: github-advisory

## Affected
- Maven: `org.jenkinsci.plugins.spoonscript:spoonscript` — affected >=0

## Details
A missing permission check in Jenkins TurboScript Plugin 1.3 and earlier allows attackers with Item/Read permission to trigger builds of jobs corresponding to the attacker-specified repository.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2023-30532
- https://www.jenkins.io/security/advisory/2023-04-12/#SECURITY-2851
- http://www.openwall.com/lists/oss-security/2023/04/13/3
