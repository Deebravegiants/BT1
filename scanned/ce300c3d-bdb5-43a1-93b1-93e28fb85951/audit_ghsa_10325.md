# [M] Server-Side Request Forgery (SSRF) in Craft CMS with Asset Uploads Mutations

## Summary
Severity: Medium
Advisory: GHSA-3m9m-24vh-39wx
CVE: CVE-2026-41129
CWE: CWE-918
Ecosystem: Packagist
CVSS: CVSS:4.0/AV:N/AC:L/AT:N/PR:H/UI:N/VC:H/VI:L/VA:N/SC:N/SI:N/SA:N/E:P (CVSS_V4)
Published: 2026-04-14
Source: https://github.com/advisories/GHSA-3m9m-24vh-39wx
Type: github-advisory

## Affected
- Packagist: `craftcms/cms` — affected >=5.0.0-RC1 <5.9.15
- Packagist: `craftcms/cms` — affected >=4.0.0-RC1 <4.17.9

## Details
## Required Permissions

The exploitation requires a few permissions to be enabled in the used GraphQL schema:

* "Edit assets in the <VolumeName> volume"
* "Create assets in the <VolumeName> volume"

## Details

The implementation fails to restrict the URL Scheme. While the application is intended to "upload assets", there is no whitelist forcing `http` or `https`. This allows attackers to use the Gopher protocol to wrap raw TCP commands.

**Impact:** Combined with the DWORD bypass, an attacker can hit internal services without triggering any "127.0.0.1" string-matching filters.

**Example Payload:** gopher://2130706433:6379/_FLUSHALL (Targets local Redis via DWORD).

**Remediation Strategy**

To prevent mathematical IP obfuscation, the application must normalize the hostname before validation.

## References
- https://github.com/craftcms/cms/security/advisories/GHSA-3m9m-24vh-39wx
- https://nvd.nist.gov/vuln/detail/CVE-2026-41129
- https://github.com/craftcms/cms/commit/d20aecfaa0eae076c4154be3b17e1f9fa05ce46f
- https://github.com/craftcms/cms
