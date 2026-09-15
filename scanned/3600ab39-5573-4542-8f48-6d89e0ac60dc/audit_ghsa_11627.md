# [H] CraftCMS has an RCE vulnerability via relational conditionals in the control panel

## Summary
Severity: High
Advisory: GHSA-fp5j-j7j4-mcxc
CVE: CVE-2026-31857
CWE: CWE-94
Ecosystem: Packagist
CVSS: CVSS:4.0/AV:N/AC:L/AT:N/PR:N/UI:N/VC:H/VI:H/VA:H/SC:N/SI:N/SA:N/E:U (CVSS_V4)
Published: 2026-03-11
Source: https://github.com/advisories/GHSA-fp5j-j7j4-mcxc
Type: github-advisory

## Affected
- Packagist: `craftcms/cms` — affected >=5.0.0-RC1 <5.9.9
- Packagist: `craftcms/cms` — affected >=4.0.0-beta.1 <4.17.4

## Details
A Remote Code Execution vulnerability exists in the Craft CMS 5 conditions system.

The `BaseElementSelectConditionRule::getElementIds()` method passes user-controlled string input
through `renderObjectTemplate()` -- an unsandboxed Twig rendering function with escaping disabled.

Any authenticated Control Panel user (including non-admin roles such as Author or Editor) can achieve full
RCE by sending a crafted condition rule via standard element listing endpoints.

This vulnerability requires no admin privileges, no special permissions beyond basic control panel access, and
bypasses all production hardening settings (allowAdminChanges: false, devMode: false,
enableTwigSandbox: true).

Users should update to the patched 5.99 release to mitigate the issue.

## References
- https://github.com/craftcms/cms/security/advisories/GHSA-fp5j-j7j4-mcxc
- https://nvd.nist.gov/vuln/detail/CVE-2026-31857
- https://github.com/craftcms/cms/commit/8d4903647dcfd31b8d40ed027e27082013347a80
- https://github.com/craftcms/cms
