# [M] Kirby's page creation API bypasses the changeStatus permission check via unfiltered isDraft parameter

## Summary
Severity: Medium
Advisory: GHSA-w942-j9r6-hr6r
CVE: CVE-2026-40099
CWE: CWE-863
Ecosystem: Packagist
CVSS: CVSS:4.0/AV:N/AC:L/AT:N/PR:L/UI:N/VC:N/VI:L/VA:N/SC:N/SI:N/SA:N (CVSS_V4)
Published: 2026-04-23
Source: https://github.com/advisories/GHSA-w942-j9r6-hr6r
Type: github-advisory

## Affected
- Packagist: `getkirby/cms` — affected >=0 <4.9.0
- Packagist: `getkirby/cms` — affected >=5.0.0 <5.4.0

## Details
### TL;DR

This vulnerability affects all Kirby sites where users have the permission to create pages (`pages.create` permission is enabled) but not the permission to change the status of pages (`pages.changeStatus` permission is disabled). This can be due to configuration in the user blueprint(s), via `options` in the page blueprint(s) or via a combination of both settings.

Users' Kirby sites are *not* affected if their use case does not consider the creation of published pages a malicious action. The vulnerability can only be exploited by authenticated users.

----

### Introduction

An authorization bypass allows authenticated users to perform actions they should not be allowed to perform based on their configured permissions, thereby causing a privilege escalation.

The effects of an authorization bypass can include unauthorized access to sensitive information as well as unauthorized changes to content or system information.

### Impact

Kirby's user permissions control which user role is allowed to perform specific actions to content models in the CMS. These permissions are defined for each role in the user blueprint (`site/blueprints/users/...`). It is also possible to customize the permissions for each target model in the model blueprints (such as in `site/blueprints/pages/...`) using the `options` feature. The permissions and options together control the authorization of user actions.

For pages, Kirby provides the `pages.create` and `pages.changeStatus` permissions (among others). In affected releases, Kirby checked these permissions independently and only for the respective action. However the `changeStatus` permission didn't take effect on page creation.

New pages are created as drafts by default and need to be published by changing the page status of an existing page draft. This is ensured when the page is created via the Kirby Panel. However the REST API allows to override the `isDraft` flag when creating a new page. This allowed authenticated attackers with the `pages.create` permission to immediately create published pages, bypassing the normal editorial workflow.

### Patches

The problem has been patched in [Kirby 4.9.0](https://github.com/getkirby/kirby/releases/tag/4.9.0) and [Kirby 5.4.0](https://github.com/getkirby/kirby/releases/tag/5.4.0). Please update to one of these or a [later version](https://github.com/getkirby/kirby/releases) to fix the vulnerability.

In all of the mentioned releases, Kirby has added a check to the page creation rules that ensures that users without the `pages.changeStatus` permission cannot create published pages, only page drafts.

### Credits

Kirby thanks @offset for responsibly reporting the identified issue.

## References
- https://github.com/getkirby/kirby/security/advisories/GHSA-w942-j9r6-hr6r
- https://nvd.nist.gov/vuln/detail/CVE-2026-40099
- https://github.com/getkirby/kirby
- https://github.com/getkirby/kirby/releases/tag/4.9.0
- https://github.com/getkirby/kirby/releases/tag/5.4.0
