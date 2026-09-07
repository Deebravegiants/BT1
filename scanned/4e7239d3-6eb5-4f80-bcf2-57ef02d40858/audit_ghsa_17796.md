# [M] Carbon has an arbitrary file include via unvalidated input passed to Carbon::setLocale

## Summary
Severity: Medium
Advisory: GHSA-j3f9-p6hm-5w6q
CVE: CVE-2025-22145
CWE: CWE-98
Ecosystem: Packagist
CVSS: CVSS:4.0/AV:N/AC:L/AT:P/PR:N/UI:N/VC:L/VI:L/VA:L/SC:N/SI:N/SA:N (CVSS_V4)
Published: 2025-01-08
Source: https://github.com/advisories/GHSA-j3f9-p6hm-5w6q
Type: github-advisory

## Affected
- Packagist: `nesbot/carbon` — affected >=3.0.0 <3.8.4
- Packagist: `nesbot/carbon` — affected >=0 <2.72.6

## Details
### Impact
Application passing unsanitized user input to `Carbon::setLocale` are at risk of arbitrary file include, if the application allows users to upload files with `.php` extension in an folder that allows `include` or `require` to read it, then they are at risk of arbitrary code ran on their servers.

### Patches
- [3.8.4](https://github.com/briannesbitt/Carbon/releases/tag/3.8.4)
- [2.72.6](https://github.com/briannesbitt/Carbon/releases/tag/2.72.6)

### Workarounds
Any of the below actions can be taken to prevent the issue:
- Validate input before calling `setLocale()`, for instance by forbidding or removing `/` and `\`
- Call `setLocale()` only with a locale from a whitelist of supported locales
- When uploading files, rename them so they cannot have a `.php` extension (this is recommended even if you're not affected by this issue)
- Prefer storage system that are not local to the application (remote service, or local service ran by another user so the uploaded files actually live outside of the application basedir)

### References
https://en.wikipedia.org/wiki/File_inclusion_vulnerability

### Credits
Thanks to **Szczepan Hołyszewski** who reported the issue and to Tidelift to coordinate the resolution

## References
- https://github.com/CarbonPHP/carbon/security/advisories/GHSA-j3f9-p6hm-5w6q
- https://nvd.nist.gov/vuln/detail/CVE-2025-22145
- https://github.com/briannesbitt/Carbon/commit/129700ed449b1f02d70272d2ac802357c8c30c58
- https://github.com/CarbonPHP/carbon
- https://lists.debian.org/debian-lts-announce/2025/02/msg00032.html
