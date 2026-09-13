# [H] Kirby CMS's `pages.access/list` and `files.access/list` permissions are not consistently checked in the Panel and REST API

## Summary
Severity: High
Advisory: GHSA-85x2-r8xv-ww8c
CVE: CVE-2026-42137
CWE: CWE-862, CWE-863
Ecosystem: Packagist
CVSS: CVSS:4.0/AV:N/AC:L/AT:N/PR:L/UI:N/VC:H/VI:N/VA:N/SC:N/SI:N/SA:N (CVSS_V4)
Published: 2026-04-30
Source: https://github.com/advisories/GHSA-85x2-r8xv-ww8c
Type: github-advisory

## Affected
- Packagist: `getkirby/cms` — affected >=0 <4.9.0
- Packagist: `getkirby/cms` — affected >=5.0.0 <5.4.0

## Details
### TL;DR

This vulnerability affects all Kirby sites where users of a particular role have no permission to access or list pages or files (`pages.access`, `pages.list`, `files.access` or `files.list` permission is disabled). This can be due to configuration in the user blueprint(s), via `options` in the model blueprint(s) or via a combination of both settings.

**This vulnerability is of high severity for affected sites.**

Consumers' Kirby sites are *not* affected if they intend all users to be able to access all pages and files of the site. The vulnerability can only be exploited by authenticated users. Write actions are *not* affected by this vulnerability.

----

### Introduction

Missing authorization allows authenticated users to perform actions they are not intended to have access to.

The effects of missing authorization can include unauthorized access to sensitive information as well as unauthorized changes to content or system information.

### Impact

Kirby's user permissions control which user role is allowed to perform specific actions to content models in the CMS. These permissions are defined for each role in the user blueprint (`site/blueprints/users/...`). It is also possible to customize the permissions for each target model in the model blueprints (such as in `site/blueprints/pages/...`) using the `options` feature. The permissions and options together control the authorization of user actions.

Kirby provides the `pages.access`, `pages.list`, `files.access` and `files.list` permissions (among others). The `list` permissions control whether affected models appear in lists throughout the Panel and REST API. The `access` permissions have the same effect but also disable direct access to the affected models.

In affected releases, Kirby did not consistently hide non-listable models (models for which the respective `access` or `list` permission was disabled) in the following scenarios:

- The changes dialog in the Panel listed changed models even if they were not listable.
- The REST API respected the permissions during direct model access, but did not consistently filter collections as well as related models that are included in the API responses for convenience. This includes:
  - missing permission checks for children, drafts, files, parents and siblings of pages,
  - missing permission checks for parents and siblings (`next`/`nextWithTemplate `, `prev`/`prevWithTemplate`) of files,
  - missing permission checks for children, drafts and files of the site model,
  - missing permission checks for files of users,
  - incorrect permission checks for `pages.access` instead of `pages.list` for the site and pages children and search routes and
  - incorrect permission checks for `files.access` instead of `files.list` for the account, site, pages and users files and search routes,
- The Panel images for site, pages and users were displayed in lists of the parent model even if the image files were not listable.
- The link targets for the previous and next files in the files view were not gated by the files being listable.

### Patches

The problem has been patched in [Kirby 4.9.0](https://github.com/getkirby/kirby/releases/tag/4.9.0) and [Kirby 5.4.0](https://github.com/getkirby/kirby/releases/tag/5.4.0). Please update to one of these or a [later version](https://github.com/getkirby/kirby/releases) to fix the vulnerability.

In all of the mentioned releases, we have added permission checks for `$model->isListable()` in all of the affected places. This ensures that results are filtered by the listable property, thereby enforcing the `pages.access`, `pages.list`, `files.access` and `files.list` permissions consistently.

## References
- https://github.com/getkirby/kirby/security/advisories/GHSA-85x2-r8xv-ww8c
- https://github.com/getkirby/kirby
- https://github.com/getkirby/kirby/releases/tag/4.9.0
- https://github.com/getkirby/kirby/releases/tag/5.4.0
