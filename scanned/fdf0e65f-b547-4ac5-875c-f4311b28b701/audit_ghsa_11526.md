# [M] Craft CMS has potential authenticated Remote Code Execution via Twig SSTI

## Summary
Severity: Medium
Advisory: GHSA-qc86-q28f-ggww
CVE: CVE-2026-28784
CWE: CWE-1336
Ecosystem: Packagist
CVSS: CVSS:4.0/AV:N/AC:L/AT:N/PR:H/UI:N/VC:H/VI:H/VA:H/SC:N/SI:N/SA:N/E:U (CVSS_V4)
Published: 2026-03-03
Source: https://github.com/advisories/GHSA-qc86-q28f-ggww
Type: github-advisory

## Affected
- Packagist: `craftcms/cms` — affected >=5.0.0-RC1 <5.9.0-beta.1
- Packagist: `craftcms/cms` — affected >=4.0.0-RC1 <4.17.0-beta.1

## Details
For this to work, the attacker must have administrator access to the Craft Control Panel, and [allowAdminChanges](https://craftcms.com/docs/5.x/reference/config/general.html#allowadminchanges) must be enabled, which is against Craft CMS' recommendations for any non-dev environment.

https://craftcms.com/knowledge-base/securing-craft#set-allowAdminChanges-to-false-in-production

Alternatively, they can have a non-administrator account with `allowAdminChanges` disabled, but they must have access to the System Messages utility.

It is possible to craft a malicious payload using the Twig `map` filter in text fields that accept Twig input under Settings in the Craft control panel or using the System Messages utility, which could lead to a RCE.

Users should update to the patched versions (5.8.22 and 4.16.18) to mitigate the issue.

References:

https://github.com/craftcms/cms/pull/18208

## References
- https://github.com/craftcms/cms/security/advisories/GHSA-qc86-q28f-ggww
- https://nvd.nist.gov/vuln/detail/CVE-2026-28784
- https://github.com/craftcms/cms/pull/18208
- https://craftcms.com/knowledge-base/securing-craft#set-allowAdminChanges-to-false-in-production
- https://github.com/craftcms/cms
