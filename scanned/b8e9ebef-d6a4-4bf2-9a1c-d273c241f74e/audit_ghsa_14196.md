# [M] Jenkins Quay.io trigger Plugin webhook endpoint can be accessed without authentication

## Summary
Severity: Medium
Advisory: GHSA-q2fc-9ww2-ggfj
CVE: CVE-2023-30519
CWE: CWE-862
Ecosystem: Maven
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:L/A:N (CVSS_V3)
Published: 2023-04-12
Source: https://github.com/advisories/GHSA-q2fc-9ww2-ggfj
Type: github-advisory

## Affected
- Maven: `org.jenkins-ci.plugins:quayio-trigger` — affected >=0

## Details
Jenkins Quay.io trigger Plugin provides a webhook endpoint at `/quayio-webhook/` that can be used to trigger builds of jobs configured to use a specified repository.

In Quay.io trigger Plugin 0.1 and earlier, this endpoint can be accessed without authentication.

This allows unauthenticated attackers to trigger builds of jobs corresponding to the attacker-specified repository.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2023-30519
- https://www.jenkins.io/security/advisory/2023-04-12/#SECURITY-2849
- http://www.openwall.com/lists/oss-security/2023/04/13/3
