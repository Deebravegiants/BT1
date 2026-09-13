# [H] CVE-2020-1597

## Summary
Severity: High
Advisory: CVE-2020-1597
Aliases: BIT-aspnet-core-2020-1597, GHSA-f8qx-mjcq-wfgx
CVSS: 7.5 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:H)
Published: 2020-08-17
Source: https://osv.dev/vulnerability/CVE-2020-1597
Type: osv

## Details
A denial of service vulnerability exists when ASP.NET Core improperly handles web requests. An attacker who successfully exploited this vulnerability could cause a denial of service against an ASP.NET Core web application. The vulnerability can be exploited remotely, without authentication.
A remote unauthenticated attacker could exploit this vulnerability by issuing specially crafted requests to the ASP.NET Core application.
The update addresses the vulnerability by correcting how the ASP.NET Core web application handles web requests.

## References
- https://lists.fedoraproject.org/archives/list/package-announce%40lists.fedoraproject.org/message/WH5FQ5VT3JGHXFXOETHCTBWJUIAPGHHT/
- https://lists.fedoraproject.org/archives/list/package-announce%40lists.fedoraproject.org/message/ZW4CBI26KSO3PRL3HLVVISXPPOYUHSXO/
- https://portal.msrc.microsoft.com/en-US/security-guidance/advisory/CVE-2020-1597
