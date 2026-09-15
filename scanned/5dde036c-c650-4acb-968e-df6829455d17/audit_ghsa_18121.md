# [H] Command Injection via sonarqube-scan-action GitHub Action

## Summary
Severity: High
Advisory: GHSA-f79p-9c5r-xg88
CVE: CVE-2025-58178
CWE: CWE-77
Ecosystem: GitHub Actions
CVSS: CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H (CVSS_V3)
Published: 2025-09-02
Source: https://github.com/advisories/GHSA-f79p-9c5r-xg88
Type: github-advisory

## Affected
- GitHub Actions: `SonarSource/sonarqube-scan-action` — affected >=4.0.0 <5.3.1

## Details
### Impact
A command injection vulnerability was discovered in the SonarQube Scan GitHub Action that allows untrusted input arguments to be processed without proper sanitization. Arguments sent to the action are treated as shell expressions, allowing potential execution of arbitrary commands.

### Patches
A fix has been released in SonarQube Scan GitHub Action v5.3.1.

## References
- https://github.com/SonarSource/sonarqube-scan-action/security/advisories/GHSA-f79p-9c5r-xg88
- https://github.com/SonarSource/sonarqube-scan-action/pull/200
- https://github.com/SonarSource/sonarqube-scan-action/commit/016cabf33a6b7edf0733e179a03ad408ad4e88ba
- https://community.sonarsource.com/t/security-advisory-sonarqube-scanner-github-action/147696
- https://github.com/SonarSource/sonarqube-scan-action
- https://sonarsource.atlassian.net/browse/SQSCANGHA-101
