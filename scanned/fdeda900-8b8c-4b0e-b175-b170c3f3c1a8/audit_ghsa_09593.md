# [H] Kirby is vulnerable to authorization bypass during page, file and user creation via blueprint injection

## Summary
Severity: High
Advisory: GHSA-6gqr-mx34-wh8r
CVE: CVE-2026-41325
CWE: CWE-863
Ecosystem: Packagist
CVSS: CVSS:4.0/AV:N/AC:L/AT:N/PR:L/UI:N/VC:N/VI:H/VA:N/SC:N/SI:N/SA:N (CVSS_V4)
Published: 2026-04-24
Source: https://github.com/advisories/GHSA-6gqr-mx34-wh8r
Type: github-advisory

## Affected
- Packagist: `getkirby/cms` — affected >=0 <4.9.0
- Packagist: `getkirby/cms` — affected >=5.0.0 <5.4.0

## Details
### TL;DR

This vulnerability affects all Kirby sites where users of a particular role have no permission to create pages, files or users (`pages.create`, `files.create` or `users.create` permission is disabled). This can be due to configuration in the user blueprint(s), via `options` in the model blueprint(s) or via a combination of both settings.

**This vulnerability is of high severity for affected sites.**

Developers' Kirby sites are *not* affected if they intend all users of their site to be able to create pages, files and users. The vulnerability can only be exploited by authenticated users.

----

### Introduction

An authorization bypass allows authenticated users to perform actions they should not be allowed to perform based on their configured permissions, thereby causing a privilege escalation.

The effects of an authorization bypass can include unauthorized access to sensitive information as well as unauthorized changes to content or system information.

### Impact

Kirby's user permissions control which user role is allowed to perform specific actions to content models in the CMS. These permissions are defined for each role in the user blueprint (`site/blueprints/users/...`). It is also possible to customize the permissions for each target model in the model blueprints (such as in `site/blueprints/pages/...`) using the `options` feature. The permissions and options together control the authorization of user actions.

Kirby provides the `pages.create`, `files.create` and `users.create` permissions (among others). These permissions can again be set in the user blueprint and/or in the blueprint of the target model via `options`. In affected releases, Kirby allowed to override the `options` during the creation of pages, files and users by injecting custom dynamic blueprint configuration into the model data. The injected `options` could include `'create' => true`, which then caused an override of the permissions and options configured by the site developer in the user and model blueprints.

### Patches

The problem has been patched in [Kirby 4.9.0](https://github.com/getkirby/kirby/releases/tag/4.9.0) and [Kirby 5.4.0](https://github.com/getkirby/kirby/releases/tag/5.4.0). Please update to one of these or a [later version](https://github.com/getkirby/kirby/releases) to fix the vulnerability.

In all of the mentioned releases, we have updated the normalization code that is used during the creation of pages, files and users to include a filter for the `blueprint` property. This prevents the injection of dynamic blueprint configuration into the creation request.

### Credits

Kirby thanks @offset for responsibly reporting the identified issue.

## References
- https://github.com/getkirby/kirby/security/advisories/GHSA-6gqr-mx34-wh8r
- https://nvd.nist.gov/vuln/detail/CVE-2026-41325
- https://github.com/getkirby/kirby
- https://github.com/getkirby/kirby/releases/tag/4.9.0
- https://github.com/getkirby/kirby/releases/tag/5.4.0
