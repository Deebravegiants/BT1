# [M] Umbraco.AI discloses sensitive application configuration values

## Summary
Severity: Medium
Advisory: GHSA-q3v2-xj35-9grx
CWE: CWE-200
Ecosystem: NuGet
CVSS: CVSS:3.1/AV:N/AC:L/PR:H/UI:N/S:U/C:H/I:N/A:N (CVSS_V3)
Published: 2026-07-14
Source: https://github.com/advisories/GHSA-q3v2-xj35-9grx
Type: github-advisory

## Affected
- NuGet: `Umbraco.AI` — affected >=0 <1.14.0

## Details
### Impact
Under certain configurations, a user with elevated privileges may be able to cause sensitive application configuration values, potentially including secret material such as credentials, to be disclosed. Successful exploitation could expose confidential information and, depending on what the affected installation stores in configuration, enable further compromise. Exploitation requires access to the AI section of the backoffice and a specific custom AI provider, which limits real-world exposure.

### Patches
Patched in 1.14.0

### Workarounds
Since the patch is a breaking change and requires a version jump, it is not recommended to try and implement a workaround.

### Resources
* Announcement Blog Post: https://umbraco.com/blog/security-advisory-june-4-2026-security-patch-for-umbracoai-is-now-available/

## References
- https://github.com/umbraco/Umbraco.AI/security/advisories/GHSA-q3v2-xj35-9grx
- https://github.com/umbraco/Umbraco.AI
- https://github.com/umbraco/Umbraco.AI/releases/tag/2026.06.2
- https://umbraco.com/blog/security-advisory-june-4-2026-security-patch-for-umbracoai-is-now-available
