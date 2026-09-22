# [H] Flarum vulnerable to LFI and Blind SSRF via Avatar upload

## Summary
Severity: High
Advisory: GHSA-67c6-q4j4-hccg
CVE: CVE-2023-40033
CWE: CWE-918, CWE-98
Ecosystem: Packagist
CVSS: CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:H/I:L/A:N (CVSS_V3)
Published: 2023-08-16
Source: https://github.com/advisories/GHSA-67c6-q4j4-hccg
Type: github-advisory

## Affected
- Packagist: `flarum/core` — affected >=0 <1.8.0
- Packagist: `flarum/framework` — affected >=0 <1.8.0

## Details
## Impact
The Flarum forum software is affected by a vulnerability that allows an attacker to conduct a Blind SSRF attack or disclose any file on the server, even with a basic user account on any Flarum forum. By uploading a file containing a URL and spoofing the MIME type, an attacker can manipulate the application to execute unintended actions. The vulnerability is due to the behavior of the `intervention/image` package, which attempts to interpret the supplied file contents as a URL, which then fetches its contents. This allows an attacker to exploit the vulnerability to perform SSRF attacks, disclose local file contents, or conduct a blind oracle attack.

### Patches
This has been patched in Flarum **v1.8**.

## Workarounds
As a temporary workaround for the SSRF aspect of the vulnerability, one can disable PHP's `allow_url_fopen` which will prevent the fetching of external files via URLs.

### Credits
Adam Kues - [Assetnote](https://assetnote.io/)

## References
- https://github.com/flarum/framework/security/advisories/GHSA-67c6-q4j4-hccg
- https://nvd.nist.gov/vuln/detail/CVE-2023-40033
- https://github.com/flarum/framework/commit/d1059c1cc79fe61f9538f3da55e8f42abbede570
- https://github.com/flarum/framework
