# [H] discordi.js is malware

## Summary
Severity: High
Advisory: GHSA-fv9m-f7w4-889c
CVE: CVE-2017-16207
CWE: CWE-506
Ecosystem: npm
CVSS: CVSS:3.0/AV:N/AC:L/PR:N/UI:N/S:U/C:L/I:L/A:L (CVSS_V3)
Published: 2018-08-06
Source: https://github.com/advisories/GHSA-fv9m-f7w4-889c
Type: github-advisory

## Affected
- npm: `discordi.js` — affected >=0

## Details
The `discordi.js` package is malware that attempts to discover and exfiltrate a user's [Discord](https://discordapp.com/) credentials, sending them to pastebin.

All versions have been unpublished from the npm registry.


## Recommendation

Do not install / use this module. It has been unpublished from the npm registry but may exist in some caches. Any users that logged into Discord using this library will need to change their credentials.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2017-16207
- https://github.com/advisories/GHSA-fv9m-f7w4-889c
- https://www.npmjs.com/advisories/545
