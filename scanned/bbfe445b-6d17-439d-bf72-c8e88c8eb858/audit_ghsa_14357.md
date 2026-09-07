# [M] Cross Site Scripting (XSS) in Serenity

## Summary
Severity: Medium
Advisory: GHSA-93h6-wx7r-mgfp
CVE: CVE-2023-31285
CWE: CWE-79
Ecosystem: NuGet
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:R/S:C/C:L/I:L/A:N (CVSS_V3)
Published: 2023-04-27
Source: https://github.com/advisories/GHSA-93h6-wx7r-mgfp
Type: github-advisory

## Affected
- NuGet: `Serenity.Net.Core` — affected >=0 <6.7.0
- NuGet: `Serenity.Net.Services` — affected >=0 <6.7.0

## Details
An XSS issue was discovered in Serenity Serene (and StartSharp) before 6.7.0. When users upload temporary files, some specific file endings are not allowed, but it is possible to upload .html or .htm files containing an XSS payload. The resulting link can be sent to an administrator user.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2023-31285
- https://github.com/serenity-is/Serenity/commit/11b9d267f840513d04b4f4d4876de7823a6e48d2
- https://github.com/serenity-is/Serenity/commit/f54e9bfcf8ceb7f26f81a7362349bc1f63251d92
- https://github.com/serenity-is/serene/commit/6dce8162f4382badd429a9f0f1470acb64e8c4fd
- https://github.com/serenity-is/Serenity
- http://packetstormsecurity.com/files/172648/Serenity-StartSharp-Software-File-Upload-XSS-User-Enumeration-Reusable-Tokens.html
- http://seclists.org/fulldisclosure/2023/May/14
