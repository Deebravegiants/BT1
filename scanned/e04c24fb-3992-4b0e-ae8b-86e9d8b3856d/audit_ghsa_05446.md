# [M] Umbraco.Forms has Path Traversal and File Enumeration Vulnerabilities in Linux/Mac

## Summary
Severity: Medium
Advisory: GHSA-hm5p-82g6-m3xh
CVE: CVE-2026-24687
CWE: CWE-22
Ecosystem: NuGet
CVSS: CVSS:4.0/AV:N/AC:L/AT:P/PR:L/UI:N/VC:H/VI:N/VA:N/SC:N/SI:N/SA:N (CVSS_V4)
Published: 2026-01-30
Source: https://github.com/advisories/GHSA-hm5p-82g6-m3xh
Type: github-advisory

## Affected
- NuGet: `Umbraco.Forms` — affected >=16.0.0 <16.4.1
- NuGet: `Umbraco.Forms` — affected >=17.0.0 <17.1.1

## Details
### Impact
It's possible for an authenticated backoffice-user to enumerate and traverse paths/files on the systems filesystem and read their contents, on Mac/Linux Umbraco installations using Forms. As Umbraco Cloud runs in a Windows environment, Cloud users aren't affected. 

### Patches
This issue affects versions 16 and 17 of Umbraco Forms and is patched in 16.4.1 and 17.1.1

### Workarounds
If upgrading is not immediately possible, users can mitigate this vulnerability by:
* Configuring a WAF or reverse proxy to block requests containing path traversal sequences (`../`, `..\`) in the `fileName` parameter of the export endpoint
* Restricting network access to the Umbraco backoffice to trusted IP ranges
* Blocking the `/umbraco/forms/api/v1/export` endpoint entirely if the export feature is not required

However, upgrading to the patched version is strongly recommended.

### References
Credit to Kevin Joensen from Baldur Security for finding this vulnerability

## References
- https://github.com/umbraco/Umbraco.Forms.Issues/security/advisories/GHSA-hm5p-82g6-m3xh
- https://nvd.nist.gov/vuln/detail/CVE-2026-24687
- https://github.com/umbraco/Umbraco.Forms.Issues
