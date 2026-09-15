# [M] User account enumeration in Serenity

## Summary
Severity: Medium
Advisory: GHSA-w7jm-9x4m-8qc3
CVE: CVE-2023-31286
CWE: CWE-209
Ecosystem: NuGet
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:L/I:N/A:N (CVSS_V3)
Published: 2023-04-27
Source: https://github.com/advisories/GHSA-w7jm-9x4m-8qc3
Type: github-advisory

## Affected
- NuGet: `Serenity.Net.Core` — affected >=0 <6.7.0
- NuGet: `Serenity.Net.Web` — affected >=0 <6.7.0

## Details
An issue was discovered in Serenity Serene (and StartSharp) before 6.7.0. When a password reset request occurs, the server response leaks the existence of users. If one tries to reset a password of a non-existent user, an error message indicates that this user does not exist.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2023-31286
- https://github.com/serenity-is/Serenity/commit/11b9d267f840513d04b4f4d4876de7823a6e48d2
- https://github.com/serenity-is/Serenity
- https://seclists.org/fulldisclosure/2023/May/14
- http://packetstormsecurity.com/files/172648/Serenity-StartSharp-Software-File-Upload-XSS-User-Enumeration-Reusable-Tokens.html
- http://seclists.org/fulldisclosure/2023/May/14
