# [H] Jenkins WSO2 Oauth Plugin Session Fixation vulnerability

## Summary
Severity: High
Advisory: GHSA-xxq2-74hw-vg6m
CVE: CVE-2023-33005
CWE: CWE-384, CWE-613
Ecosystem: Maven
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:R/S:U/C:H/I:H/A:H (CVSS_V3)
Published: 2023-05-16
Source: https://github.com/advisories/GHSA-xxq2-74hw-vg6m
Type: github-advisory

## Affected
- Maven: `org.jenkins-ci.plugins:wso2id-oauth` — affected >=0

## Details
Jenkins WSO2 Oauth Plugin 1.0 and earlier does not invalidate the existing session on login.

This allows attackers to use social engineering techniques to gain administrator access to Jenkins.

As of publication of this advisory, there is no fix.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2023-33005
- https://www.jenkins.io/security/advisory/2023-05-16/#SECURITY-2991
