# [H] CVE-2024-47807

## Summary
Severity: High
Advisory: CVE-2024-47807
Aliases: GHSA-8pjw-fff6-3mjv
CVSS: 8.1 (CVSS:3.1/AV:N/AC:H/PR:N/UI:N/S:U/C:H/I:H/A:H)
Published: 2024-10-02
Source: https://osv.dev/vulnerability/CVE-2024-47807
Type: osv

## Details
Jenkins OpenId Connect Authentication Plugin 4.354.v321ce67a_1de8 and earlier does not check the `iss` (Issuer) claim of an ID Token, allowing attackers to subvert the authentication flow, potentially gaining administrator access to Jenkins.

## References
- https://www.jenkins.io/security/advisory/2024-10-02/#SECURITY-3441%20(2)
