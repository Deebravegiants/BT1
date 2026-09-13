# [M] Kirby: `pages.access` permission is not checked in the pages picker for parent pages

## Summary
Severity: Medium
Advisory: GHSA-23q2-54qv-rq5x
CVE: CVE-2026-49274
CWE: CWE-862
Ecosystem: Packagist
CVSS: CVSS:4.0/AV:N/AC:L/AT:N/PR:L/UI:N/VC:L/VI:N/VA:N/SC:N/SI:N/SA:N (CVSS_V4)
Published: 2026-06-18
Source: https://github.com/advisories/GHSA-23q2-54qv-rq5x
Type: github-advisory

## Affected
- Packagist: `getkirby/cms` — affected >=0 <4.9.4
- Packagist: `getkirby/cms` — affected >=5.0.0-alpha.1 <5.4.4

## Details
### TL;DR

This vulnerability affects all Kirby sites that use the `pages` field and where users of a particular role have no permission to access pages (`pages.access` permission is disabled). This can be due to configuration in the user blueprint(s), `options` in the model blueprint(s), or a combination of both settings.

It was possible to confirm the existence of arbitrary pages and to retrieve the value of the title field of the pages found.

The vulnerability can only be exploited by authenticated users. Write actions are *not* affected by this vulnerability.

----

### Introduction

Missing authorization allows authenticated users to perform actions they are not intended to have access to.

The effects of missing authorization can include unauthorized access to sensitive information as well as unauthorized changes to content or system information.

### Affected components

Kirby's user permissions control which user role is allowed to perform specific actions on content models in the CMS. These permissions are defined for each role in the user blueprint (`site/blueprints/users/...`). It is also possible to customize the permissions for each target model in the model blueprints (such as in `site/blueprints/pages/...`) using the `options` feature. The permissions and options together control the authorization of user actions.

Kirby provides the `pages.access` and `pages.list` permissions (among others). The `list` permission controls whether affected models appear in lists throughout the Panel and REST API. The `access` permission has the same effect but also disables direct access to the affected models.

This vulnerability affects the backend logic for the page picker that is used in the `pages` field to select pages. The picker is opened based on a user-provided parent page or the site model.

### Impact

In affected releases, the backend logic did not validate that the user-provided parent page or site was accessible to the current user. This allowed authenticated attackers with knowledge of the full path to an existing page to confirm the existence of a particular page and to retrieve the value of the title field of that page. This could lead to the disclosure of sensitive information.

### Patches

The problem has been patched in [Kirby 4.9.4](https://github.com/getkirby/kirby/releases/tag/4.9.4) and [Kirby 5.4.4](https://github.com/getkirby/kirby/releases/tag/5.4.4). Please update to one of these or a [later version](https://github.com/getkirby/kirby/releases) to fix the vulnerability.

In all of the mentioned releases, we have added a check verifying that the requested parent page or site is accessible to the current user before returning the picker data.

## References
- https://github.com/getkirby/kirby/security/advisories/GHSA-23q2-54qv-rq5x
- https://github.com/getkirby/kirby
- https://github.com/getkirby/kirby/releases/tag/4.9.4
- https://github.com/getkirby/kirby/releases/tag/5.4.4
