# [H] Craft CMS: Potential authenticated Remote Code Execution via referrer redirect

## Summary
Severity: High
Advisory: GHSA-f74w-488g-8x5r
CVE: CVE-2026-55794
CWE: CWE-94
Ecosystem: Packagist
CVSS: CVSS:4.0/AV:N/AC:L/AT:N/PR:L/UI:N/VC:H/VI:H/VA:H/SC:L/SI:L/SA:L (CVSS_V4)
Published: 2026-07-06
Source: https://github.com/advisories/GHSA-f74w-488g-8x5r
Type: github-advisory

## Affected
- Packagist: `craftcms/cms` — affected >=5.9.0 <5.10.0

## Details
### Requirements:

* Control panel access
* Permissions to edit an entry

### Details

Control panel users with the ability to edit entries can execute unsandboxed Twig code via the HTTP Referrer header.

The issue happens when a user is saving entries. Strings for a signed redirect URL are being compiled as a Twig template via `renderObjectTemplate()`, and while a sandboxed alternative already exists (`renderSandboxedObjectTemplate()`), it is not used in this case. This signed URL can be specified by users, as it is reflected in the “Referer” HTTP request header, which is under attacker control.

This has been fixed in Craft 5.10.0. Affected users should update to that version or higher to get the fix.

### Resources

https://github.com/craftcms/cms/pull/18680

## References
- https://github.com/craftcms/cms/security/advisories/GHSA-f74w-488g-8x5r
- https://nvd.nist.gov/vuln/detail/CVE-2026-55794
- https://github.com/craftcms/cms/pull/18680
- https://github.com/craftcms/cms
