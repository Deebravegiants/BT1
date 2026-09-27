# [H] dalorRadius full account take over

## Summary
Severity: High
Advisory: CVE-2022-23475
Aliases: GHSA-c9xx-6mvw-9v84
CVSS: 8.8 (CVSS:3.1/AV:N/AC:L/PR:N/UI:R/S:U/C:H/I:H/A:H)
Published: 2022-12-06
Source: https://osv.dev/vulnerability/CVE-2022-23475
Type: osv

## Details
daloRADIUS is an open source RADIUS web management application. daloRadius 1.3 and prior are vulnerable to a combination cross site scripting (XSS) and cross site request forgery (CSRF) vulnerability which leads to account takeover in the mng-del.php file because of an unescaped variable reflected in the DOM on line 116. This issue has been addressed in commit `ec3b4a419e`. Users are advised to manually apply the commit in order to mitigate this issue. Users may also mitigate this issue with in two parts 1) The CSRF vulnerability can be mitigated  by making the daloRadius session cookie to samesite=Lax or by the implimentation of a CSRF token in all forms. 2) The XSS vulnerability may be mitigated by escaping it or by introducing a Content-Security policy.

## References
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2022/23xxx/CVE-2022-23475.json
- https://github.com/lirantal/daloradius/security/advisories/GHSA-c9xx-6mvw-9v84
- https://nvd.nist.gov/vuln/detail/CVE-2022-23475
- https://github.com/lirantal/daloradius/commit/ec3b4a419e20540cf28ce60e48998b893e3f1dea
