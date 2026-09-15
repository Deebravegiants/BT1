# [H] CVE-2020-1161

## Summary
Severity: High
Advisory: CVE-2020-1161
Aliases: BIT-aspnet-core-2020-1161, GHSA-3cf7-7wq6-8842
CVSS: 7.5 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:H)
Published: 2020-05-21
Source: https://osv.dev/vulnerability/CVE-2020-1161
Type: osv

## Details
A denial of service vulnerability exists when ASP.NET Core improperly handles web requests. An attacker who successfully exploited this vulnerability could cause a denial of service against an ASP.NET Core web application. The vulnerability can be exploited remotely, without authentication.
A remote unauthenticated attacker could exploit this vulnerability by issuing specially crafted requests to the ASP.NET Core application.
The update addresses the vulnerability by correcting how the ASP.NET Core web application handles web requests.

## References
- https://msrc.microsoft.com/update-guide/vulnerability/CVE-2020-1161
- https://portal.msrc.microsoft.com/en-US/security-guidance/advisory/CVE-2020-1161
