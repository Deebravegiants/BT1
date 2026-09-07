# [M] Jenkins WSO2 Oauth Plugin cross-site request forgery vulnerability

## Summary
Severity: Medium
Advisory: GHSA-7xgj-j9hp-c692
CVE: CVE-2023-33006
CWE: CWE-352
Ecosystem: Maven
CVSS: CVSS:3.1/AV:N/AC:L/PR:L/UI:R/S:U/C:L/I:L/A:N (CVSS_V3)
Published: 2023-05-16
Source: https://github.com/advisories/GHSA-7xgj-j9hp-c692
Type: github-advisory

## Affected
- Maven: `org.jenkins-ci.plugins:wso2id-oauth` — affected >=0

## Details
Jenkins WSO2 Oauth Plugin 1.0 and earlier does not implement a state parameter in its OAuth flow, a unique and non-guessable value associated with each authentication request. 

This vulnerability allows attackers to trick users into logging in to the attacker’s account.

As of publication of this advisory, there is no fix.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2023-33006
- https://www.jenkins.io/security/advisory/2023-05-16/#SECURITY-2990
