# [C] Command Injection in macaddress

## Summary
Severity: Critical
Advisory: GHSA-pp57-mqmh-44h7
CVE: CVE-2018-13797
CWE: CWE-78
Ecosystem: npm
CVSS: CVSS:3.0/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H (CVSS_V3)
Published: 2018-09-06
Source: https://github.com/advisories/GHSA-pp57-mqmh-44h7
Type: github-advisory

## Affected
- npm: `macaddress` — affected >=0 <0.2.9

## Details
All versions of `macaddress` are vulnerable to command injection. For this vulnerability to be exploited an attacker needs to control the `iface` argument to the `one` method.


## Recommendation

Update to version 0.2.9 or later.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2018-13797
- https://github.com/scravy/node-macaddress/pull/20
- https://github.com/scravy/node-macaddress/commit/358fd594adb196a86b94ac9c691f69fe5dad2332
- https://hackerone.com/reports/319467
- https://github.com/advisories/GHSA-pp57-mqmh-44h7
- https://github.com/scravy/node-macaddress
- https://github.com/scravy/node-macaddress/releases/tag/0.2.9
- https://news.ycombinator.com/item?id=17283394
- https://www.npmjs.com/advisories/654
