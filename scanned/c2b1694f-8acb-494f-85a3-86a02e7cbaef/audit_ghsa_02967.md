# [M] Cross-site scripting (XSS) from writer field content in the site frontend

## Summary
Severity: Medium
Advisory: GHSA-x7j7-qp7j-hw3q
CVE: CVE-2021-41252
CWE: CWE-79
Ecosystem: Packagist
CVSS: CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:L/I:L/A:N (CVSS_V3)
Published: 2021-11-16
Source: https://github.com/advisories/GHSA-x7j7-qp7j-hw3q
Type: github-advisory

## Affected
- Packagist: `getkirby/cms` — affected >=3.5.0 <3.5.8

## Details
### Impact

Kirby's [writer field](https://getkirby.com/docs/reference/panel/fields/writer) stores its formatted content as HTML code. Unlike with other field types, it is not possible to [escape HTML special characters](https://getkirby.com/docs/guide/templates/escaping) against cross-site scripting (XSS) attacks, otherwise the formatting would be lost.

Cross-site scripting (XSS) is a type of vulnerability that allows to execute any kind of JavaScript code inside the site frontend or Panel session of other users. If the user is logged in to the Panel, a harmful script can for example trigger requests to Kirby's API with the permissions of the victim.

Because the writer field did not securely sanitize its contents on save, it was possible to inject malicious HTML code into the content file by sending it to Kirby's API directly without using the Panel. This malicious HTML code would then be displayed on the site frontend and executed in the browsers of site visitors and logged in users who are browsing the site.

This vulnerability is critical if you might have potential attackers in your group of authenticated Panel users. They can escalate their privileges if they get access to the Panel session of an admin user. Depending on your site, other JavaScript-powered attacks are possible.

You are *not* affected if you don't use the writer field in any of your blueprints. The attack can only be performed by logged-in users and only surfaces in the site frontend (i.e. in your templates). The Panel itself is unaffected and will not execute JavaScript that was injected into writer field content.

### Patches

We have patched the vulnerability in [Kirby 3.5.8](https://github.com/getkirby/kirby/releases/tag/3.5.8) by sanitizing all writer field contents on the backend whenever the content is modified via Kirby's API. Please update to this or a [later version](https://github.com/getkirby/kirby/releases/) to fix the vulnerability.

### Credits

Thanks to Azrul Ikhwan Zulkifli (@azrultech) from BAE Systems AI Vulnerability Research Team for responsibly reporting the identified issue.

## References
- https://github.com/getkirby/kirby/security/advisories/GHSA-x7j7-qp7j-hw3q
- https://nvd.nist.gov/vuln/detail/CVE-2021-41252
- https://github.com/getkirby/kirby/commit/25fc5c6b330442e6433c99befc688f3698c5d1fc
- https://github.com/getkirby/kirby
- https://github.com/getkirby/kirby/releases/tag/3.5.8
