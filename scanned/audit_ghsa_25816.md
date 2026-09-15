# [H] Server side request forgery in C1 CMS

## Summary
Severity: High
Advisory: GHSA-8pp6-8x4q-c5mx
CVE: CVE-2022-24789
CWE: CWE-918
Ecosystem: NuGet
CVSS: CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:L/I:L/A:H (CVSS_V3)
Published: 2022-03-30
Source: https://github.com/advisories/GHSA-8pp6-8x4q-c5mx
Type: github-advisory

## Affected
- NuGet: `C1CMS.Assemblies` — affected >=0 <6.12.8122.18346

## Details
C1 CMS is an open-source, .NET based Content Management System (CMS). Versions prior to 6.12 allow an authenticated user to exploit Server Side Request Forgery (SSRF) by causing the server to make arbitrary GET requests to other servers in the local network or on localhost. The attacker may also truncate arbitrary files to zero size (effectively delete them) leading to denial of service (DoS) or altering application logic. The authenticated user may unknowingly perform the actions by visiting a specially crafted site. Patched in C1 CMS v6.12, no known workarounds exist.

## References
- https://github.com/Orckestra/C1-CMS-Foundation/security/advisories/GHSA-j9c2-gr6m-pp45
- https://nvd.nist.gov/vuln/detail/CVE-2022-24789
- https://github.com/Orckestra/C1-CMS-Foundation
- https://github.com/Orckestra/C1-CMS-Foundation/releases/tag/v6.12
