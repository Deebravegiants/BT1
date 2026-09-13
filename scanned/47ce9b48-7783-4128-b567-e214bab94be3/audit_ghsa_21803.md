# [M] Missing permission check in Jenkins Conjur Secrets Plugin allows enumerating credentials IDs

## Summary
Severity: Medium
Advisory: GHSA-372f-jc47-7gr5
CVE: CVE-2022-25190
CWE: CWE-862
Ecosystem: Maven
CVSS: CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:L/I:N/A:N (CVSS_V3)
Published: 2022-02-16
Source: https://github.com/advisories/GHSA-372f-jc47-7gr5
Type: github-advisory

## Affected
- Maven: `org.conjur.jenkins:conjur-credentials` — affected >=0 <1.0.12

## Details
Conjur Secrets Plugin 1.0.11 and earlier does not perform a permission check in an HTTP endpoint.

This allows attackers with Overall/Read permission to enumerate credentials IDs of credentials stored in Jenkins. Those can be used as part of an attack to capture the credentials using another vulnerability.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2022-25190
- https://github.com/jenkinsci/conjur-credentials-plugin/commit/eda06cde26cdf2d40ae4e2f4d2709e8174489068
- https://github.com/jenkinsci/conjur-credentials-plugin
- https://www.jenkins.io/security/advisory/2022-02-15/#SECURITY-2350
