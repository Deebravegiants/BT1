# [H] Jenkins WSO2 Oauth Plugin Fails to Properly Authenticate User Credentials

## Summary
Severity: High
Advisory: GHSA-p89h-p4ph-4vj6
CVE: CVE-2025-47889
CWE: CWE-1390, CWE-287
Ecosystem: Maven
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H (CVSS_V3)
Published: 2025-05-14
Source: https://github.com/advisories/GHSA-p89h-p4ph-4vj6
Type: github-advisory

## Affected
- Maven: `org.jenkins-ci.plugins:wso2id-oauth` — affected >=0

## Details
In Jenkins WSO2 Oauth Plugin 1.0 and earlier, authentication claims are accepted without validation by the "WSO2 Oauth" security realm, allowing unauthenticated attackers to log in to controllers using this security realm using any username and any password, including usernames that do not exist.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2025-47889
- https://www.jenkins.io/security/advisory/2025-05-14/#SECURITY-3481
