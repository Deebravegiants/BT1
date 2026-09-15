# [H] Insufficient token expiration in Serenity

## Summary
Severity: High
Advisory: GHSA-2hp9-3xfr-r9w2
CVE: CVE-2023-31287
CWE: CWE-640
Ecosystem: NuGet
CVSS: CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H (CVSS_V3)
Published: 2023-04-27
Source: https://github.com/advisories/GHSA-2hp9-3xfr-r9w2
Type: github-advisory

## Affected
- NuGet: `Serenity.Net.Core` — affected >=0 <6.7.0
- NuGet: `Serenity.Net.Web` — affected >=0 <6.7.0

## Details
An issue was discovered in Serenity Serene (and StartSharp) before 6.7.0. Password reset links are sent by email. A link contains a token that is used to reset the password. This token remains valid even after the password reset and can be used a second time to change the password of the corresponding user. The token expires only 3 hours after issuance and is sent as a query parameter when resetting. An attacker with access to the browser history can thus use the token again to change the password in order to take over the account.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2023-31287
- https://github.com/serenity-is/Serenity/commit/11b9d267f840513d04b4f4d4876de7823a6e48d2
- https://github.com/serenity-is/Serenity
- https://packetstorm.news/files/id/172648
- http://packetstormsecurity.com/files/172648/Serenity-StartSharp-Software-File-Upload-XSS-User-Enumeration-Reusable-Tokens.html
- http://seclists.org/fulldisclosure/2023/May/14
