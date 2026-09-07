# [M] Kirby Panel users could upload PHP Phar archives as content files before v2.5.14 and v3.4.5

## Summary
Severity: Medium
Advisory: GHSA-g3h8-cg9x-47qw
CVE: CVE-2020-26255
CWE: CWE-434
Ecosystem: Packagist
CVSS: CVSS:3.1/AV:N/AC:L/PR:H/UI:N/S:C/C:N/I:H/A:N (CVSS_V3)
Published: 2020-12-08
Source: https://github.com/advisories/GHSA-g3h8-cg9x-47qw
Type: github-advisory

## Affected
- Packagist: `getkirby/panel` — affected >=0 <2.5.14
- Packagist: `getkirby/cms` — affected >=3.0.0 <3.4.5

## Details
### Impact

An editor with full access to the Kirby Panel can upload a PHP `.phar` file and execute it on the server. This vulnerability is critical if you might have potential attackers in your group of authenticated Panel users, as they can gain access to the server with such a Phar file.

Visitors without Panel access *cannot* use this attack vector.

### Patches

The problem has been patched in [Kirby 2.5.14](https://github.com/getkirby-v2/panel/releases/tag/2.5.14) and [Kirby 3.4.5](https://github.com/getkirby/kirby/releases/tag/3.4.5). Please update to one of these or a [later version](https://github.com/getkirby/kirby/releases/) to fix the vulnerability.

**Note:** Kirby 2 reaches end of life on December 31, 2020. We therefore recommend to upgrade your Kirby 2 sites to Kirby 3. If you cannot upgrade, we still recommend to update to Kirby 2.5.14.

### Workarounds

Kirby 2 sites on older releases can also be patched by applying the [changes from this commit](https://github.com/getkirby-v2/panel/commit/5a569d4e3ddaea2b6628d7ec1472a3e8bc410881).

### Credits

Thanks to Thore Imhof of Accenture for reporting the problem.

## References
- https://github.com/getkirby/kirby/security/advisories/GHSA-g3h8-cg9x-47qw
- https://nvd.nist.gov/vuln/detail/CVE-2020-26255
- https://github.com/getkirby-v2/panel/commit/5a569d4e3ddaea2b6628d7ec1472a3e8bc410881
- https://github.com/getkirby/kirby/commit/db8f371b13036861c9cc5ba3e85e27f73fce5e09
- https://github.com/getkirby/kirby
- https://github.com/getkirby/kirby/releases/tag/3.4.5
- https://packagist.org/packages/getkirby/cms
- https://packagist.org/packages/getkirby/panel
