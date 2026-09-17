# [M] Kirby: Access to files of top-level drafts is not protected by permissions

## Summary
Severity: Medium
Advisory: GHSA-89cp-7p28-jffg
CVE: CVE-2026-54004
CWE: CWE-862
Ecosystem: Packagist
CVSS: CVSS:4.0/AV:N/AC:L/AT:P/PR:N/UI:N/VC:L/VI:N/VA:N/SC:N/SI:N/SA:N (CVSS_V4)
Published: 2026-06-18
Source: https://github.com/advisories/GHSA-89cp-7p28-jffg
Type: github-advisory

## Affected
- Packagist: `getkirby/cms` — affected >=0 <4.9.4
- Packagist: `getkirby/cms` — affected >=5.0.0-alpha.1 <5.4.4

## Details
### TL;DR

This vulnerability affects Kirby 5 sites that have the `content.fileRedirects` option enabled (set to `true` or a custom closure) as well as all Kirby 4 sites that haven't explicitly disabled this option.

It was possible to access clean file URLs of top-level drafts (e.g. `/about-us/team.jpg`) without providing authentication, without being authorized to access the top-level draft page, and without providing a valid preview token.

Sites on Kirby 5 using the default configuration are *not* affected by this vulnerability (the `content.fileRedirects` option is disabled by default since Kirby 5.0.0). It was also *not* possible to maliciously access clean file URLs for files stored in page drafts that are not on the top-level (such as `/blog/article/resource.pdf`).

----

### Introduction

Missing authorization allows authenticated users to perform actions they are not intended to have access to.

The effects of missing authorization can include unauthorized access to sensitive information as well as unauthorized changes to content or system information.

### Affected components

Clean file redirects allow visitors to access files stored in the content folder via natural URLs such as `/about-us/team.jpg` or `/blog/article/resource.pdf`. Kirby detects such requests and redirects them to the actual physical file URLs in the `media` folder.

Kirby 4.8.0 introduced the `content.fileRedirects` option that allowed disabling this behavior to protect against third-party access to original source files. Kirby 5.0.0 then made the secure behavior (disabled option) the default. It is also possible to set the option to a closure to dynamically control access for each individual file.

Files can be stored in pages. Pages can exist as drafts. In this draft state, the page preview is only accessible to users who are authenticated and authorized by the `pages.access` permission or to visitors who have received the direct preview URL with a valid preview token.

### Impact

In affected releases, the clean file redirects didn't take access logic for drafts into account. When a file stored in a draft page was accessed via its clean file URL, Kirby immediately redirected to the physical media URL without first checking whether the draft page was accessible to the user or visitor. This only affected top-level drafts (direct children of the site) because clean file URLs currently don't work for drafts that are nested under another page.

The unauthorized clean file URL redirects for files in top-level drafts can lead to disclosure of sensitive information or data, e.g., ahead of the launch of a new product or post.

A successful attack requires knowledge of the full path to the draft page and file, and therefore requires knowing the full clean file URL.

### Patches

The problem has been patched in [Kirby 4.9.4](https://github.com/getkirby/kirby/releases/tag/4.9.4) and [Kirby 5.4.4](https://github.com/getkirby/kirby/releases/tag/5.4.4). Please update to one of these or a [later version](https://github.com/getkirby/kirby/releases) to fix the vulnerability.

In all of the mentioned releases, we added an authorization check to the route that redirects clean file URLs of drafts. This route now performs the same checks as the draft preview route, i.e., it only performs the redirect if a user is logged in and has the `pages.access` permission on the draft, or if a valid preview token was provided in the request URL.

### Credits

Thanks to @adamyordan for responsibly reporting the identified issue.

## References
- https://github.com/getkirby/kirby/security/advisories/GHSA-89cp-7p28-jffg
- https://github.com/getkirby/kirby
- https://github.com/getkirby/kirby/releases/tag/4.9.4
- https://github.com/getkirby/kirby/releases/tag/5.4.4
