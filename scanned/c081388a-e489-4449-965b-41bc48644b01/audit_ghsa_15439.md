# [H] Kirby has insufficient permission checks in the language settings

## Summary
Severity: High
Advisory: GHSA-jm9m-rqr3-wfmh
CVE: CVE-2024-41964
CWE: CWE-863
Ecosystem: Packagist
CVSS: CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:N/I:H/A:H (CVSS_V3)
Published: 2024-08-29
Source: https://github.com/advisories/GHSA-jm9m-rqr3-wfmh
Type: github-advisory

## Affected
- Packagist: `getkirby/cms` — affected >=0 <3.6.6.6
- Packagist: `getkirby/cms` — affected >=3.7.0 <3.7.5.5
- Packagist: `getkirby/cms` — affected >=3.8.0 <3.8.4.4
- Packagist: `getkirby/cms` — affected >=3.9.0 <3.9.8.2
- Packagist: `getkirby/cms` — affected >=3.10.0 <3.10.1.1
- Packagist: `getkirby/cms` — affected >=4.0.0 <4.3.1

## Details
### TL;DR

This vulnerability affects all Kirby sites with enabled `languages` option that might have potential attackers in the group of authenticated Panel users.

If you have disabled the `languages` and/or `api` option and don't call any methods in your code that cause a write access to languages (language creation, update or deletion), your site is *not* affected.

----

### Introduction

Kirby allows to restrict the permissions of specific user roles. Users of that role can only perform permitted actions.

Permissions for creating and deleting languages have already existed and could be configured, but were not enforced by Kirby's frontend or backend code.

A permission for updating existing languages has not existed before the patched versions. So disabling the `languages.*` wildcard permission for a role could not have prohibited updates to existing language definitions.

### Impact

The missing permission checks allowed attackers with Panel access to manipulate the language definitions.

The language definitions are at the core of multi-language content in Kirby. Unauthorized modifications with malicious intent can cause significant damage, for example:

- If the `languages` option was enabled but no language exists, creating the first language will switch Kirby to multi-language mode.
- Deleting an existing language will lead to content loss of all translated content in that language. Deleting the last language will switch Kirby to single-language mode.
- Updating a language allows to change the metadata including the language slug (used in page URLs) and language variables. It also allows to change the default language, which will cause Kirby to use the new default language's content as a fallback for non-existing translations.

Depending on the site code, the result of such actions can cause loss of site availability (e.g. error messages in the site frontend) or integrity (due to changed URLs or removed translations).

### Patches

The problem has been patched in [Kirby 3.6.6.6](https://github.com/getkirby/kirby/releases/tag/3.6.6.6), [Kirby 3.7.5.5](https://github.com/getkirby/kirby/releases/tag/3.7.5.5), [Kirby 3.8.4.4](https://github.com/getkirby/kirby/releases/tag/3.8.4.4), [Kirby 3.9.8.2](https://github.com/getkirby/kirby/releases/tag/3.9.8.2), [Kirby 3.10.1.1](https://github.com/getkirby/kirby/releases/tag/3.10.1.1), and [Kirby 4.3.1](https://github.com/getkirby/kirby/releases/tag/4.3.1). Please update to one of these or a [later version](https://github.com/getkirby/kirby/releases) to fix the vulnerability.

In all of the mentioned releases, we have added checks for the `languages.create` and `languages.delete` permissions that ensure that users without those permissions cannot perform the respective actions. We have also added a new `languages.update` permission.

### Credits

Thanks to Sebastian Eberlein of JUNO (@SebastianEberlein-JUNO) for reporting the identified issue.

## References
- https://github.com/getkirby/kirby/security/advisories/GHSA-jm9m-rqr3-wfmh
- https://nvd.nist.gov/vuln/detail/CVE-2024-41964
- https://github.com/getkirby/kirby/commit/1dbc9215c97a5c22dc7f34a4e3a64d19e1eac151
- https://github.com/getkirby/kirby/commit/38636655b054e820f66c3b717c55a9d60fe6400a
- https://github.com/getkirby/kirby/commit/83fce501759782cf843b6f1d9293a7c7167e69af
- https://github.com/getkirby/kirby/commit/ab95d172667c3cd529917c2bc94d3c7969706d23
- https://github.com/getkirby/kirby/commit/af9b0a58dea63effab85525ae217faa1f5ded423
- https://github.com/getkirby/kirby/commit/e647a177c75636ef4824662b2ce00d8e5c3a8406
- https://github.com/getkirby/kirby
- https://github.com/getkirby/kirby/releases/tag/3.10.1.1
- https://github.com/getkirby/kirby/releases/tag/3.6.6.6
- https://github.com/getkirby/kirby/releases/tag/3.7.5.5
- https://github.com/getkirby/kirby/releases/tag/3.8.4.4
- https://github.com/getkirby/kirby/releases/tag/3.9.8.2
- https://github.com/getkirby/kirby/releases/tag/4.3.1
