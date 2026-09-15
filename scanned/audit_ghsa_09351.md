# [M] Kirby CMS's `pages.access` permission is not checked during rendering of page drafts

## Summary
Severity: Medium
Advisory: GHSA-2xw4-v2wx-hqq9
CVE: CVE-2026-44176
CWE: CWE-862
Ecosystem: Packagist
CVSS: CVSS:4.0/AV:N/AC:L/AT:P/PR:L/UI:N/VC:H/VI:N/VA:N/SC:N/SI:N/SA:N (CVSS_V4)
Published: 2026-05-26
Source: https://github.com/advisories/GHSA-2xw4-v2wx-hqq9
Type: github-advisory

## Affected
- Packagist: `getkirby/cms` — affected >=0 <4.9.1
- Packagist: `getkirby/cms` — affected >=5.0.0 <5.4.1

## Details
### TL;DR

This vulnerability affects all Kirby sites where users of a particular role have no permission to access pages (`pages.access` permission is disabled). This can be due to configuration in the user blueprint(s), via `options` in the model blueprint(s) or via a combination of both settings.

Kirby sites are *not* affected if they intend all users of the site to be able to access all page drafts of the site. The vulnerability can only be exploited by authenticated users. Write actions are *not* affected by this vulnerability.

----

### Introduction

Missing authorization allows authenticated users to perform actions they are not intended to have access to.

The effects of missing authorization can include unauthorized access to sensitive information as well as unauthorized changes to content or system information.

### Affected components

Kirby's user permissions control which user role is allowed to perform specific actions to content models in the CMS. These permissions are defined for each role in the user blueprint (`site/blueprints/users/...`). It is also possible to customize the permissions for each target model in the model blueprints (such as in `site/blueprints/pages/...`) using the `options` feature. The permissions and options together control the authorization of user actions.

Kirby provides the `pages.access` and `pages.list` permissions (among others). The `list` permission controls whether affected models appear in lists throughout the Panel and REST API. The `access` permission has the same effect but also disables direct access to the affected models.

This vulnerability affects the path resolver for the main CMS router. The resolver takes an input path from the requested URL and determines which model (page or file) should be rendered. When a path is requested that points to a page draft, the resolver checks that the request either contains a valid preview token or is authenticated by a valid user.

### Impact

In affected releases, Kirby allowed page drafts to be rendered if any valid user was authenticated, even if that user did not have access to the specific page model. Authenticated attackers with knowledge of the full path to an existing page draft could then access the rendered frontend page. This could lead to the disclosure of sensitive information, e.g. ahead of the launch of a new product or post.

### Patches

The problem has been patched in [Kirby 4.9.1](https://github.com/getkirby/kirby/releases/tag/4.9.1) and [Kirby 5.4.1](https://github.com/getkirby/kirby/releases/tag/5.4.1). Please update to one of these or a [later version](https://github.com/getkirby/kirby/releases) to fix the vulnerability.

In all of the mentioned releases, Kirby has added a check that verifies that the requested page draft is accessible to the current user before rendering the draft template.

### Credits

Kirby thank to @adrgs for responsibly reporting the identified issue.

## References
- https://github.com/getkirby/kirby/security/advisories/GHSA-2xw4-v2wx-hqq9
- https://github.com/getkirby/kirby
- https://github.com/getkirby/kirby/releases/tag/4.9.1
- https://github.com/getkirby/kirby/releases/tag/5.4.1
