# [M] Kirby XSS Vulnerability

## Summary
Severity: Medium
Advisory: GHSA-275c-v3rc-xghx
CVE: CVE-2017-16807
CWE: CWE-79
Ecosystem: Packagist
CVSS: CVSS:3.0/AV:N/AC:L/PR:L/UI:R/S:C/C:L/I:L/A:N (CVSS_V3)
Published: 2022-05-14
Source: https://github.com/advisories/GHSA-275c-v3rc-xghx
Type: github-advisory

## Affected
- Packagist: `getkirby/cms` — affected >=0 <2.3.3
- Packagist: `getkirby/cms` — affected >=2.4 <2.4.2
- Packagist: `getkirby/cms` — affected >=2.5 <2.5.7

## Details
A cross-site Scripting (XSS) vulnerability in Kirby Panel before 2.3.3, 2.4.x before 2.4.2, and 2.5.x before 2.5.7 exists when displaying a specially prepared SVG document that has been uploaded as a content file.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2017-16807
- https://getkirby.com/changelog/kirby-2-5-7
- https://packetstormsecurity.com/files/144965/KirbyCMS-Cross-Site-Scripting.html
- https://www.exploit-db.com/exploits/43140
