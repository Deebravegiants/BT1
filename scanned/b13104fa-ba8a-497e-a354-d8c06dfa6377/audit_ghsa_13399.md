# [M] Cross-site scripting (XSS) from MIME type auto-detection of uploaded files

## Summary
Severity: Medium
Advisory: GHSA-8fv7-wq38-f5c9
CVE: CVE-2023-38491
CWE: CWE-79
Ecosystem: Packagist
CVSS: CVSS:3.1/AV:N/AC:L/PR:L/UI:R/S:U/C:H/I:N/A:N (CVSS_V3)
Published: 2023-07-28
Source: https://github.com/advisories/GHSA-8fv7-wq38-f5c9
Type: github-advisory

## Affected
- Packagist: `getkirby/cms` — affected >=0 <3.5.8.3
- Packagist: `getkirby/cms` — affected >=3.6.0 <3.6.6.3
- Packagist: `getkirby/cms` — affected >=3.7.0 <3.7.5.2
- Packagist: `getkirby/cms` — affected >=3.8.0 <3.8.4.1
- Packagist: `getkirby/cms` — affected >=3.9.0 <3.9.6

## Details
### TL;DR

This vulnerability affects all Kirby sites that might have potential attackers in the group of authenticated Panel users or that allow external visitors to upload an arbitrary file to the content folder.

Your Kirby sites are *not* affected if they don't allow file uploads for untrusted users or visitors or if the file extensions of uploaded files are limited to a fixed safe list.

The attack requires user interaction by another user or visitor and *cannot* be automated.

----

### Introduction

Cross-site scripting (XSS) is a type of vulnerability that allows to execute any kind of JavaScript code inside the Panel session of the same or other users. In the Panel, a harmful script can for example trigger requests to Kirby's API with the permissions of the victim.

Such vulnerabilities are critical if you might have potential attackers in your group of authenticated Panel users. They can escalate their privileges if they get access to the Panel session of an admin user. Depending on your site, other JavaScript-powered attacks are possible.

### Impact

An editor with write access to the Kirby Panel could upload a file with an unknown file extension like `.xyz` that contains HTML code including harmful content like `<script>` tags. The direct link to that file could be sent to other users or visitors of the site. If the victim opened that link in a browser where they are logged in to Kirby and the file had not been opened by anyone since the upload, Kirby would serve the file with an incorrect MIME type of `text/html`. The browser would then run the script, which could for example trigger requests to Kirby's API with the permissions of the victim.

The issue was caused by the underlying `Kirby\Http\Response::file()` method, which didn't have an explicit fallback if the MIME type could not be determined from the file extension. If you use this method in site or plugin code, these uses may be affected by the same vulnerability.

### Patches

The problem has been patched in [Kirby 3.5.8.3](https://github.com/getkirby/kirby/releases/tag/3.5.8.3), [Kirby 3.6.6.3](https://github.com/getkirby/kirby/releases/tag/3.6.6.3), [Kirby 3.7.5.2](https://github.com/getkirby/kirby/releases/tag/3.7.5.2), [Kirby 3.8.4.1](https://github.com/getkirby/kirby/releases/tag/3.8.4.1) and [Kirby 3.9.6](https://github.com/getkirby/kirby/releases/tag/3.9.6). Please update to one of these or a [later version](https://github.com/getkirby/kirby/releases) to fix the vulnerability.

In all of the mentioned releases, we have fixed the affected method to use a fallback MIME type of `text/plain` and set the `X-Content-Type-Options: nosniff` header if the MIME type of the file is unknown.

### Credits

Thanks to Shankar Acharya (@5hank4r) for responsibly reporting the identified issue.

## References
- https://github.com/getkirby/kirby/security/advisories/GHSA-8fv7-wq38-f5c9
- https://nvd.nist.gov/vuln/detail/CVE-2023-38491
- https://github.com/getkirby/kirby/commit/2f06ba1c026bc91cb0702bc16b7d505642536d15
- https://github.com/getkirby/kirby
- https://github.com/getkirby/kirby/releases/tag/3.5.8.3
- https://github.com/getkirby/kirby/releases/tag/3.6.6.3
- https://github.com/getkirby/kirby/releases/tag/3.7.5.2
- https://github.com/getkirby/kirby/releases/tag/3.8.4.1
- https://github.com/getkirby/kirby/releases/tag/3.9.6
