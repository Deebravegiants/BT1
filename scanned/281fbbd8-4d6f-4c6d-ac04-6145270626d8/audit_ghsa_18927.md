# [H] OpenAM: Using arbitrary OIDC requested claims values in id_token and user_info is allowed 

## Summary
Severity: High
Advisory: GHSA-39hr-239p-fhqc
CVE: CVE-2025-64099
CWE: CWE-74, CWE-94
Ecosystem: Maven
CVSS: CVSS:4.0/AV:N/AC:L/AT:N/PR:N/UI:N/VC:H/VI:H/VA:H/SC:N/SI:N/SA:N/E:U (CVSS_V4)
Published: 2025-11-12
Source: https://github.com/advisories/GHSA-39hr-239p-fhqc
Type: github-advisory

## Affected
- Maven: `org.openidentityplatform.openam:openam-oauth2` — affected >=0 <16.0.3

## Details
### Summary
If the "claims_parameter_supported" parameter is activated, it is possible through the "oidc-claims-extension.groovy" script, to inject the value of choice into a claim contained in the id_token or in the user_info.
Authorization function requests do not prevent a claims parameter containing a JSON file to be injected. This JSON file allows users to customize claims returned by the "id_token" and "user_info" files.
This allows for a very wide range of vulnerabilities depending on how clients use claims. For example, if some clients rely on an email field to identify a user, users can choose to entera any email address, and therefore assume any chosen identity.

## References
- https://github.com/OpenIdentityPlatform/OpenAM/security/advisories/GHSA-39hr-239p-fhqc
- https://nvd.nist.gov/vuln/detail/CVE-2025-64099
- https://github.com/OpenIdentityPlatform/OpenAM/commit/4254b34b2b8b4867f2e7fccfac73904213d48510
- https://github.com/OpenIdentityPlatform/OpenAM
- https://github.com/OpenIdentityPlatform/OpenAM/releases/tag/16.0.3
