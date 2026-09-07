# [M] Jenkins Microsoft Entra ID (previously Azure AD) Plugin has an open redirect vulnerability

## Summary
Severity: Medium
Advisory: GHSA-jp6g-g3v3-6gvf
CVE: CVE-2026-42525
CWE: CWE-601
Ecosystem: Maven
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:R/S:U/C:N/I:L/A:N (CVSS_V3)
Published: 2026-04-29
Source: https://github.com/advisories/GHSA-jp6g-g3v3-6gvf
Type: github-advisory

## Affected
- Maven: `org.jenkins-ci.plugins:azure-ad` — affected >=0 <667.v4c5827a

## Details
Jenkins Microsoft Entra ID (previously Azure AD) Plugin versions 666.v6060de32f87d and earlier do not restrict the redirect URL after login.

This allows attackers to perform phishing attacks by having users go to a Jenkins URL that will forward them to a different site after successful authentication.

Microsoft Entra ID (previously Azure AD) Plugin 667.v4c5827a_e74a_0 only redirects to relative (Jenkins) URLs.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2026-42525
- https://github.com/jenkinsci/azure-ad-plugin
- https://www.jenkins.io/security/advisory/2026-04-29/#SECURITY-3760
