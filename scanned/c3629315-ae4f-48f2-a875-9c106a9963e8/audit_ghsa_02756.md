# [H] Cross-site scripting (XSS) from field and configuration text displayed in the Panel

## Summary
Severity: High
Advisory: GHSA-2f2w-349x-vrqm
CVE: CVE-2021-32735
CWE: CWE-80
Ecosystem: Packagist
CVSS: CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:H/I:L/A:N (CVSS_V3)
Published: 2021-07-02
Source: https://github.com/advisories/GHSA-2f2w-349x-vrqm
Type: github-advisory

## Affected
- Packagist: `getkirby/cms` — affected >=0 <3.5.7

## Details
On Saturday, @hdodov reported that the Panel's `ListItem` component (used in the pages and files section for example) displayed HTML in page titles as it is. This could be used for cross-site scripting (XSS) attacks.

We used his report as an opportunity to find and fix XSS issues related to dynamic site content throughout the Panel codebase.

### Impact

Cross-site scripting (XSS) is a type of vulnerability that allows to execute any kind of JavaScript code inside the Panel session of other users. In the Panel, a harmful script can for example trigger requests to Kirby's API with the permissions of the victim.

Such vulnerabilities are critical if you might have potential attackers in your group of authenticated Panel users. They can escalate their privileges if they get access to the Panel session of an admin user. Depending on your site, other JavaScript-powered attacks are possible.

Visitors without Panel access can only use this attack vector if your site allows changing site data from a frontend form (for example user self-registration or the creation of pages from a contact or other frontend form). If you validate or sanitize the provided form data, you are already protected against such attacks by external visitors.

### Patches

[Kirby 3.5.7](https://github.com/getkirby/kirby/releases/tag/3.5.7) contains patches for the following issues we found during our investigation:

- Some translated error and info messages contain placeholders to dynamically insert information like page titles or filenames. While the translation strings are allowed to contain HTML formatting, the dynamic data needs to be protected against XSS attacks. Kirby 3.5.7 now escapes the dynamic data.
- Our `Box` component used to display information for the user supports HTML output for specific use-cases. We found out that the dialogs used in the `files`, `pages` and `users` fields as well as the `fields` section used it to display raw exception or error messages. These messages are now escaped.
- The users and settings views display user and language data using the `ListItem` component that supports HTML. We now escape the dynamic data before it is passed to the `ListItem` component.
- Some of our sections and fields support HTML for their `text`, `help` and/or `info` properties. This allows custom formatting from the blueprint, but also caused the original issue reported to us that allowed to inject HTML code from the content itself. Kirby 3.5.7 now escapes the default `text` displayed by the `files` and `pages` sections (filename/page title), the `files`, `pages` and `users` fields (filename/page title/username) and by query-based `checkboxes`, `radio`, `tags` and `multiselect` fields (default text depending on the used query).

**Note:** Custom `text`, `help` and `info` queries in blueprints are *not* escaped in 3.5.7. We support HTML in these properties because there are valid use-cases for custom formatting. However there can still be XSS vulnerabilities depending on your use of these properties. In Kirby 3.6 we will provide a new feature that will make it much easier to control whether you want to allow HTML from query placeholders.

## References
- https://github.com/getkirby/kirby/security/advisories/GHSA-2f2w-349x-vrqm
- https://nvd.nist.gov/vuln/detail/CVE-2021-32735
- https://github.com/getkirby/kirby/commit/f5ead62f8510158bed5baf58ca0e851875778a09
- https://github.com/getkirby/kirby
- https://github.com/getkirby/kirby/releases/tag/3.5.7
