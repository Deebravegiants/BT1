# [H] Kirby CMS's read access to site, user and role information is not gated by permissions

## Summary
Severity: High
Advisory: GHSA-2h7v-4372-f6x2
CVE: CVE-2026-42069
CWE: CWE-862
Ecosystem: Packagist
CVSS: CVSS:4.0/AV:N/AC:L/AT:N/PR:L/UI:N/VC:H/VI:N/VA:N/SC:N/SI:N/SA:N (CVSS_V4)
Published: 2026-05-04
Source: https://github.com/advisories/GHSA-2h7v-4372-f6x2
Type: github-advisory

## Affected
- Packagist: `getkirby/cms` — affected >=0 <4.9.0
- Packagist: `getkirby/cms` — affected >=5.0.0 <5.4.0

## Details
### TL;DR

This vulnerability affects all Kirby sites that might have potential attackers in the group of authenticated Panel users.

**This vulnerability is of high severity for affected sites.**

Sites using Kirby are *not* affected if they intend all users of the site to be able to list and access the site model and all users and roles, including the content stored within these models. Write actions are *not* affected by this vulnerability as they were gated by permissions before.

----

### Introduction

Missing authorization allows authenticated users to perform actions they are not intended to have access to.

The effects of missing authorization can include unauthorized access to sensitive information as well as unauthorized changes to content or system information.

### Impact

Kirby's user permissions control which user role is allowed to perform specific actions to content models in the CMS. These permissions are defined for each role in the user blueprint (`site/blueprints/users/...`). It is also possible to customize the permissions for each target model in the model blueprints (such as in `site/blueprints/pages/...`) using the `options` feature. The permissions and options together control the authorization of user actions.

In affected releases, Kirby did not provide permission settings that control the access to the site model as well as to users and user roles. If the site developer disabled all permissions via the wildcard `"*": false` setting, this only disabled the actions that were explicitly gated by existing permissions.

To be specific, the following permissions were missing in affected releases and have been added in the patches:

- `site.access`
- `user.access` and `users.access` (for the own user and other users respectively)
- `user.list` and `users.list` (for the own user and other users respectively)

Access to role information such as the list of existing roles, their names and descriptions as well as their configured permissions were also not gated by user-based permissions.

### Patches

The problem has been patched in [Kirby 4.9.0](https://github.com/getkirby/kirby/releases/tag/4.9.0) and [Kirby 5.4.0](https://github.com/getkirby/kirby/releases/tag/5.4.0). Please update to one of these or a [later version](https://github.com/getkirby/kirby/releases) to fix the vulnerability.

In all of the mentioned releases, Kirby has added the missing permissions that are listed in the "Impact" section. The `user.access` and `users.access` permissions also take effect on the access to the user's own role and to other roles respectively.

### Credits

Kirby thanks @HuajiHD for responsibly reporting the identified issue.

## References
- https://github.com/getkirby/kirby/security/advisories/GHSA-2h7v-4372-f6x2
- https://nvd.nist.gov/vuln/detail/CVE-2026-42069
- https://github.com/getkirby/kirby
- https://github.com/getkirby/kirby/releases/tag/4.9.0
- https://github.com/getkirby/kirby/releases/tag/5.4.0
