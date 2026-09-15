# [C] Jenkins OpenId Connect Authentication Plugin lacks audience claim validation

## Summary
Severity: Critical
Advisory: GHSA-49hx-9mm2-7675
CVE: CVE-2024-47806
CWE: CWE-287
Ecosystem: Maven
CVSS: CVSS:3.1/AV:N/AC:H/PR:N/UI:N/S:U/C:H/I:H/A:H (CVSS_V3)
Published: 2024-10-02
Source: https://github.com/advisories/GHSA-49hx-9mm2-7675
Type: github-advisory

## Affected
- Maven: `org.jenkins-ci.plugins:oic-auth` — affected >=0 <4.355.v3a

## Details
Jenkins OpenId Connect Authentication Plugin 4.354.v321ce67a_1de8 and earlier does not check the `aud` (Audience) claim of an ID Token during its authentication flow, a value to verify the token is issued for the correct client.

This vulnerability may allow attackers to subvert the authentication flow, potentially gaining administrator access to Jenkins.

OpenId Connect Authentication Plugin 4.355.v3a_fb_fca_b_96d4 checks the `aud` (Audience) claim of an ID Token during its authentication flow.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2024-47806
- https://www.jenkins.io/security/advisory/2024-10-02/#SECURITY-3441%20(1)
