# [H] Mimekit has vulnerable dependency that can lead to denial of service

## Summary
Severity: High
Advisory: GHSA-gmc6-fwg3-75m5
CWE: CWE-20
Ecosystem: NuGet
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:H (CVSS_V3)
Published: 2024-07-11
Source: https://github.com/advisories/GHSA-gmc6-fwg3-75m5
Type: github-advisory

## Affected
- NuGet: `MimeKit` — affected >=3.0.0 <4.7.1

## Details
### Summary
Denial of service vulnerability.

### Details
See: https://github.com/advisories/GHSA-447r-wph3-92pm and https://github.com/dotnet/announcements/issues/312

### PoC
Update System.Security.Cryptography.Pkcs to 8.0.1 so that the transitive dependency with the issue gets updated

### Impact
Denial of service vulnerability. Affects MimeKit (>= v3.0.0 and <= v4.7.0) when used to decrypt or verify incoming S/MIME messages as well as importing 3rd-party X.509 certificates for use with encrypting outgoing S/MIME messages.

## References
- https://github.com/jstedfast/MimeKit/security/advisories/GHSA-gmc6-fwg3-75m5
- https://github.com/dotnet/announcements/issues/312
- https://github.com/jstedfast/MimeKit/commit/aef4eda75525848b992ce5e1f9b87399000fffb6
- https://github.com/advisories/GHSA-447r-wph3-92pm
- https://github.com/jstedfast/MimeKit
