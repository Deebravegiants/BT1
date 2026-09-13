# [M] Kirby CMS doesn't gate user avatar creation, replacement and deletion with user update permissions

## Summary
Severity: Medium
Advisory: GHSA-39cp-6679-8xv2
CVE: CVE-2026-42174
CWE: CWE-862
Ecosystem: Packagist
CVSS: CVSS:4.0/AV:N/AC:L/AT:N/PR:L/UI:N/VC:N/VI:L/VA:N/SC:N/SI:N/SA:N (CVSS_V4)
Published: 2026-05-04
Source: https://github.com/advisories/GHSA-39cp-6679-8xv2
Type: github-advisory

## Affected
- Packagist: `getkirby/cms` — affected >=0 <4.9.0
- Packagist: `getkirby/cms` — affected >=5.0.0 <5.4.0

## Details
### TL;DR

This vulnerability affects all Kirby sites where users of a particular role have no permission to update user information (`user.update` or `users.update` permission is disabled). This can be due to configuration in the blueprint(s) of the acting users, via `options` in the blueprint(s) of the target users or via a combination of both settings.

Kirby sites are *not* affected if they intend all users of the site to be able to upload, replace or delete user avatars. The vulnerability can only be exploited by authenticated users.

----

### Introduction

Missing authorization allows authenticated users to perform actions they are not intended to have access to.

The effects of missing authorization can include unauthorized access to sensitive information as well as unauthorized changes to content or system information.

### Impact

Kirby's user permissions control which user role is allowed to perform specific actions to content models in the CMS. These permissions are defined for each role in the user blueprint (`site/blueprints/users/...`). It is also possible to customize the permissions for each target model using the `options` feature (for user models again in the user blueprints). The permissions and options together control the authorization of user actions.

Kirby provides the `user.update` and `users.update` permissions (among others) that control the authorization to update user information for the user's own data or the data of other users respectively. User files are separately gated by the `files.create`, `files.replace` and `files.delete` permissions (among others).

In affected releases, Kirby only checked the `files.create` and `files.delete` permissions during changes to user avatars. Even though avatars are an integral part of the user profile, they were not covered by the `user.update` and `users.update` permissions. This allowed users with just file permissions to create, replace or delete user avatars.

### Patches

The problem has been patched in [Kirby 4.9.0](https://github.com/getkirby/kirby/releases/tag/4.9.0) and [Kirby 5.4.0](https://github.com/getkirby/kirby/releases/tag/5.4.0). Please update to one of these or a [later version](https://github.com/getkirby/kirby/releases) to fix the vulnerability.

In all of the mentioned releases, we have added additional permission checks for `user.update`/`users.update` when a user avatar is created, replaced or deleted. These permission checks apply in addition to the file permission checks (`files.create`, `files.replace` and `files.delete`). When a user avatar is replaced with a file of the same type, Kirby now consistently checks the `files.replace` permission instead of a combination of `files.create` and `files.delete`.

## References
- https://github.com/getkirby/kirby/security/advisories/GHSA-39cp-6679-8xv2
- https://nvd.nist.gov/vuln/detail/CVE-2026-42174
- https://github.com/getkirby/kirby
- https://github.com/getkirby/kirby/releases/tag/4.9.0
- https://github.com/getkirby/kirby/releases/tag/5.4.0
