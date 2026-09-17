# [M] Insertion of Sensitive Information into Log File in OWASP DependencyCheck

## Summary
Severity: Medium
Advisory: GHSA-frxm-v7q3-v2wv
CVE: CVE-2024-23686
CWE: CWE-532
Ecosystem: Maven
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:L/I:N/A:N (CVSS_V3)
Published: 2024-01-20
Source: https://github.com/advisories/GHSA-frxm-v7q3-v2wv
Type: github-advisory

## Affected
- Maven: `org.owasp:dependency-check-ant` — affected >=9.0.0 <9.0.6
- Maven: `org.owasp:dependency-check-cli` — affected >=9.0.0 <9.0.6
- Maven: `org.owasp:dependency-check-maven` — affected >=9.0.0 <9.0.6

## Details
DependencyCheck for Maven 9.0.0 to 9.0.6, for CLI version 9.0.0 to 9.0.5, and for Ant versions 9.0.0 to 9.0.5, when used in debug mode, allows an attacker to recover the NVD API Key from a log file.

## References
- https://github.com/jeremylong/DependencyCheck/security/advisories/GHSA-qqhq-8r2c-c3f5
- https://nvd.nist.gov/vuln/detail/CVE-2024-23686
- https://github.com/advisories/GHSA-qqhq-8r2c-c3f5
- https://github.com/jeremylong/DependencyCheck
- https://vulncheck.com/advisories/vc-advisory-GHSA-qqhq-8r2c-c3f5
