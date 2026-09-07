# [M] Cross-site scripting from dynamic options in the multiselect field

## Summary
Severity: Medium
Advisory: GHSA-3f89-869f-5w76
CVE: CVE-2022-36037
CWE: CWE-79
Ecosystem: Packagist
CVSS: CVSS:3.1/AV:N/AC:H/PR:L/UI:N/S:U/C:H/I:L/A:N (CVSS_V3)
Published: 2022-08-29
Source: https://github.com/advisories/GHSA-3f89-869f-5w76
Type: github-advisory

## Affected
- Packagist: `getkirby/cms` — affected >=0 <3.5.8.1

## Details
### Introduction

Cross-site scripting (XSS) is a type of vulnerability that allows to execute any kind of JavaScript code inside the Panel session of the same or other users. In the Panel, a harmful script can for example trigger requests to Kirby's API with the permissions of the victim.

Such vulnerabilities are critical if you might have potential attackers in your group of authenticated Panel users. They can escalate their privileges if they get access to the Panel session of an admin user. Depending on your site, other JavaScript-powered attacks are possible.

### Impact

The multiselect field allows to select tags from an autocompleted list. Unfortunately, the Panel in Kirby 3.5 used HTML rendering for the raw option value.

This allowed **attackers with influence on the options source** (e.g. content of sibling pages or an API endpoint) to inject HTML code. If a page in the Panel that uses the manipulated multiselect options was visited by a victim and the victim opened the autocomplete dropdown, the victim's browser will then have rendered this malicious HTML code.

You are *not* affected by this vulnerability if you don't use the multiselect field or only use it with options that cannot be manipulated by attackers.

### Patches

The problem has been patched in [Kirby 3.5.8.1](https://github.com/getkirby/kirby/releases/tag/3.5.8.1). Please update to this or a [later version](https://github.com/getkirby/kirby/releases) to fix the vulnerability.

### Workarounds

We recommend to update to the patch release. If you cannot update immediately, you can work around the issue by disabling the multiselect field. This can be done by uncommenting this field from all your blueprints.

## References
- https://github.com/getkirby/kirby/security/advisories/GHSA-3f89-869f-5w76
- https://nvd.nist.gov/vuln/detail/CVE-2022-36037
- https://github.com/getkirby/kirby/commit/b5b8863885e17556abc070dde1e20aec15fbfdf5
- https://github.com/getkirby/kirby
- https://github.com/getkirby/kirby/releases/tag/3.5.8.1
