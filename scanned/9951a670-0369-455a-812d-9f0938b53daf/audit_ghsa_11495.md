# [M] Craft CMS has Twig Function Blocklist Bypass

## Summary
Severity: Medium
Advisory: GHSA-5fvc-7894-ghp4
CVE: CVE-2026-28783
CWE: CWE-1336, CWE-184, CWE-94
Ecosystem: Packagist
CVSS: CVSS:4.0/AV:N/AC:L/AT:N/PR:H/UI:N/VC:H/VI:H/VA:H/SC:N/SI:N/SA:N/E:U (CVSS_V4)
Published: 2026-03-03
Source: https://github.com/advisories/GHSA-5fvc-7894-ghp4
Type: github-advisory

## Affected
- Packagist: `craftcms/cms` — affected >=5.0.0-RC1 <5.9.0-beta.1
- Packagist: `craftcms/cms` — affected >=4.0.0-RC1 <4.17.0-beta.1

## Details
Craft CMS implements a blocklist to prevent potentially dangerous PHP functions from being called via Twig non-Closure arrow functions.

In order to be able to successfully execute this attack, you need to either have `allowAdminChanges` enabled on production, or a compromised admin account, or an account with access to the System Messages utility.

Several PHP functions are not included in the blocklist, which could allow malicious actors with the required permissions to execute various types of payloads, including RCEs, arbitrary file reads, SSRFs, and SSTIs.

Twig has already deprecated this behavior, and it will eventually be removed from Twig altogether.

https://github.com/twigphp/Twig/blob/946ddeafa3c9f4ce279d1f34051af041db0e16f2/src/Extension/CoreExtension.php#L2096

This has been resolved in Craft 4.17.0 and 5.9.0, which removes the blocklist and disables all non-Clousure arrow functions in Twig globally via the `enableTwigSandbox` config setting. That setting is enabled by default on all new Craft projects. Existing Craft projects will need to enable the config setting to take advantage of it.

Existing projects should update to the patched versions of 5.9.0 and 4.17.0 to mitigate the issue and enable the config setting.

## Resources

https://github.com/craftcms/cms/pull/18208

## References
- https://github.com/craftcms/cms/security/advisories/GHSA-5fvc-7894-ghp4
- https://nvd.nist.gov/vuln/detail/CVE-2026-28783
- https://github.com/craftcms/cms/pull/18208
- https://github.com/craftcms/cms
- https://github.com/twigphp/Twig/blob/946ddeafa3c9f4ce279d1f34051af041db0e16f2/src/Extension/CoreExtension.php#L2096
