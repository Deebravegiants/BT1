# [H] Kirby: `pages.access` permission is not checked in the `site/find` REST API route

## Summary
Severity: High
Advisory: GHSA-r3w8-2c5r-h9j9
CVE: CVE-2026-54005
CWE: CWE-862
Ecosystem: Packagist
CVSS: CVSS:4.0/AV:N/AC:L/AT:N/PR:L/UI:N/VC:H/VI:N/VA:N/SC:N/SI:N/SA:N (CVSS_V4)
Published: 2026-06-18
Source: https://github.com/advisories/GHSA-r3w8-2c5r-h9j9
Type: github-advisory

## Affected
- Packagist: `getkirby/cms` — affected >=0 <4.9.4
- Packagist: `getkirby/cms` — affected >=5.0.0-alpha.1 <5.4.4

## Details
### TL;DR

This vulnerability affects all Kirby sites where users of a particular role have no permission to access pages (`pages.access` permission is disabled). This can be due to configuration in the user blueprint(s), `options` in the model blueprint(s), or a combination of both settings.

It was possible to retrieve page information (including full content and metadata) for arbitrary pages via the `/api/site/find` route without being authorized to access the respective pages.

**This vulnerability is of high severity for affected sites.**

Your Kirby sites are *not* affected if you intend all users of your site to be able to access all pages of the site. The vulnerability can only be exploited by authenticated users that know or guess the IDs or UUIDs of pages. Write actions as well as access to draft pages are *not* affected by this vulnerability.

----

### Introduction

Missing authorization allows authenticated users to perform actions they are not intended to have access to.

The effects of missing authorization can include unauthorized access to sensitive information as well as unauthorized changes to content or system information.

### Affected components

The `/api/site/find` route allows callers to request model data for a collection of user-selected pages. This model data includes structural metadata about the page itself and its children, siblings, and files and can also be extended via a query parameter to return full page content and additional metadata. The pages to return can be queried by a list of page IDs and/or UUIDs. Draft pages are excluded from this route as it only supports querying published pages.

### Impact

In affected releases, Kirby did not check whether the queried pages were accessible to the currently authenticated user.

This can lead to disclosure of sensitive information contained in inaccessible pages, including the confirmation of the existence of individual pages as well as disclosure of sensitive content fields stored in the pages. Linked children, siblings, or files were *not* affected by this vulnerability as they were already properly filtered by the appropriate `pages.list` and `files.list` permissions.

Because the `/api/site/find` route is read-only, the vulnerability does *not* allow malicious write access.

### Patches

The problem has been patched in [Kirby 4.9.4](https://github.com/getkirby/kirby/releases/tag/4.9.4) and [Kirby 5.4.4](https://github.com/getkirby/kirby/releases/tag/5.4.4). Please update to one of these or a [later version](https://github.com/getkirby/kirby/releases) to fix the vulnerability.

In all of the mentioned releases, we added a filter ensuring that the `/api/site/find` route only returns pages that are accessible to the current user.

### Credits

Thanks to Rizky Muhammad (@EvidentObscurity) for responsibly reporting the identified issue.

## References
- https://github.com/getkirby/kirby/security/advisories/GHSA-r3w8-2c5r-h9j9
- https://github.com/getkirby/kirby
- https://github.com/getkirby/kirby/releases/tag/4.9.4
- https://github.com/getkirby/kirby/releases/tag/5.4.4
