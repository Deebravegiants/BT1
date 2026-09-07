# [M] Cross-site scripting (XSS) from image block content in the site frontend

## Summary
Severity: Medium
Advisory: GHSA-cq58-r77c-5jjw
CVE: CVE-2021-41258
CWE: CWE-79, CWE-80
Ecosystem: Packagist
CVSS: CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:L/I:L/A:N (CVSS_V3)
Published: 2021-11-16
Source: https://github.com/advisories/GHSA-cq58-r77c-5jjw
Type: github-advisory

## Affected
- Packagist: `getkirby/cms` — affected >=3.5.0 <3.5.8

## Details
### Impact

Kirby's [blocks field](https://getkirby.com/docs/reference/panel/fields/blocks) stores structured data for each block. This data is then used in [block snippets](https://getkirby.com/docs/reference/panel/fields/blocks#block-snippets) to convert the blocks to HTML for use in your templates. We recommend to [escape HTML special characters](https://getkirby.com/docs/guide/templates/escaping) against cross-site scripting (XSS) attacks.

Cross-site scripting (XSS) is a type of vulnerability that allows to execute any kind of JavaScript code inside the site frontend or Panel session of other users. If the user is logged in to the Panel, a harmful script can for example trigger requests to Kirby's API with the permissions of the victim.

The default snippet for the [image block](https://getkirby.com/docs/reference/panel/blocks/image) unfortunately did not use our escaping helper. This made it possible to include malicious HTML code in the source, alt and link fields of the image block, which would then be displayed on the site frontend and executed in the browsers of site visitors and logged in users who are browsing the site.

This vulnerability is critical if you might have potential attackers in your group of authenticated Panel users. They can escalate their privileges if they get access to the Panel session of an admin user. Depending on your site, other JavaScript-powered attacks are possible.

You are *not* affected if you don't use the blocks field or specifically the image block in any of your blueprints. You are also protected if you use a custom [block snippet](https://getkirby.com/docs/reference/panel/fields/blocks#block-snippets) that either escapes the printed values or doesn't use them. The attack can only be performed by logged-in users and only surfaces in the site frontend (i.e. in your templates). The Panel itself is unaffected and will not execute JavaScript that was injected into the image block content.

### Patches

We have patched the vulnerability in [Kirby 3.5.8](https://github.com/getkirby/kirby/releases/tag/3.5.8) by escaping special HTML characters in the output from the default image block snippet. Please update to this or a [later version](https://github.com/getkirby/kirby/releases/) to fix the vulnerability.

### Credits

Thanks to Azrul Ikhwan Zulkifli (@azrultech) from BAE Systems AI Vulnerability Research Team for responsibly reporting the identified issue.

## References
- https://github.com/getkirby/kirby/security/advisories/GHSA-cq58-r77c-5jjw
- https://nvd.nist.gov/vuln/detail/CVE-2021-41258
- https://github.com/getkirby/kirby/pull/3510
- https://github.com/getkirby/kirby
- https://github.com/getkirby/kirby/releases/tag/3.5.8
