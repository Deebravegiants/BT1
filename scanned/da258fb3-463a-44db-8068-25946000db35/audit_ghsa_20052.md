# [H] Craft CMS discloses password hashes

## Summary
Severity: High
Advisory: GHSA-h972-v458-m892
CVE: CVE-2022-37783
CWE: CWE-200, CWE-522
Ecosystem: Packagist
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:N/A:N (CVSS_V3)
Published: 2022-12-05
Source: https://github.com/advisories/GHSA-h972-v458-m892
Type: github-advisory

## Affected
- Packagist: `craftcms/cms` — affected >=3.0.0 <3.7.33

## Details
All Craft CMS versions between 3.0.0 and 3.7.32 disclose password hashes of users who authenticate using their E-Mail address or username in Anti-CSRF-Tokens. Craft CMS uses a cookie called CRAFT_CSRF_TOKEN and a HTML hidden field called CRAFT_CSRF_TOKEN to avoid Cross Site Request Forgery attacks. The CRAFT_CSRF_TOKEN cookie discloses the password hash in without encoding it whereas the corresponding HTML hidden field discloses the users' password hash in a masked manner, which can be decoded by using public functions of the YII framework.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2022-37783
- https://at-trustit.tuv.at/tuev-trust-it-cves/cve-disclosure-of-password-hashes
- https://cves.at/posts/cve-2022-37783/writeup
- https://github.com/craftcms/cms
- http://www.openwall.com/lists/oss-security/2024/06/06/1
