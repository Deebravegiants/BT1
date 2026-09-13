# [H] Argument injection vulnerability in SonarQube Scan Action

## Summary
Severity: High
Advisory: GHSA-5xq9-5g24-4g6f
CVE: CVE-2025-59844
CWE: CWE-78
Ecosystem: GitHub Actions
CVSS: CVSS:4.0/AV:N/AC:L/AT:P/PR:L/UI:N/VC:H/VI:H/VA:H/SC:N/SI:N/SA:N (CVSS_V4)
Published: 2025-09-26
Source: https://github.com/advisories/GHSA-5xq9-5g24-4g6f
Type: github-advisory

## Affected
- GitHub Actions: `SonarSource/sonarqube-scan-action` — affected >=4.0.0 <6.0.0

## Details
A command injection vulnerability exists in SonarQube GitHub Action prior to v6.0.0 when workflows pass user-controlled input to the args parameter on Windows runners without proper validation. This vulnerability bypasses a previous security fix and allows arbitrary command execution, potentially leading to exposure of sensitive environment variables and compromise of the runner environment.


### Patches
The vulnerability has been fixed in version v6.0.0. Users should upgrade to this version or later.


### Credits
Francois Lajeunesse-Robert (Boostsecurity.io)


### References
- Community Post: https://community.sonarsource.com/t/sonarqube-scanner-github-action-v6/149281 
- Fix release: https://github.com/SonarSource/sonarqube-scan-action/releases/tag/v6.0.0

## References
- https://github.com/SonarSource/sonarqube-scan-action/security/advisories/GHSA-5xq9-5g24-4g6f
- https://nvd.nist.gov/vuln/detail/CVE-2025-59844
- https://community.sonarsource.com/t/sonarqube-scanner-github-action-v6/149281
- https://github.com/SonarSource/sonarqube-scan-action
- https://github.com/SonarSource/sonarqube-scan-action/releases/tag/v6.0.0
