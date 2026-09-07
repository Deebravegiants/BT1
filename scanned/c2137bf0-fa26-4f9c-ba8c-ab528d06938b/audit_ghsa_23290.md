# [M] Moodle allows attackers to bypass intended access restrictions

## Summary
Severity: Medium
Advisory: GHSA-6xpm-q8x9-j3rw
CVE: CVE-2015-5342
Ecosystem: Packagist
CVSS: CVSS:3.0/AV:N/AC:L/PR:L/UI:N/S:U/C:N/I:L/A:N (CVSS_V3)
Published: 2022-05-13
Source: https://github.com/advisories/GHSA-6xpm-q8x9-j3rw
Type: github-advisory

## Affected
- Packagist: `moodle/moodle` — affected >=0 <2.7.11
- Packagist: `moodle/moodle` — affected >=2.8.0 <2.8.9
- Packagist: `moodle/moodle` — affected >=2.9.0 <2.9.3

## Details
The choice module in Moodle through 2.6.11, 2.7.x before 2.7.11, 2.8.x before 2.8.9, and 2.9.x before 2.9.3 allows remote authenticated users to bypass intended access restrictions by visiting a URL to add or delete responses in the closed state.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2015-5342
- https://github.com/moodle/moodle/commit/02d8c8ca394ba053905f9b87c155042aabf0ce1b
- https://github.com/moodle/moodle/commit/09bb6f19e5814deb25ae6ceb8270063430b8941f
- https://github.com/moodle/moodle/commit/5c16db4fc561c97b6a907398ea081cdaf6590214
- https://github.com/moodle/moodle/commit/6283c33979001b035f9fc565b869296f66a61c4e
- https://github.com/moodle/moodle/commit/7ca8c34045eb0d2031652b452492fe4abb2c7c8a
- https://github.com/moodle/moodle/commit/97394274ee29f0a6eecab330b5bbb8ee335e7ece
- https://github.com/moodle/moodle/commit/bdaa571437c6357f322871b068f02a4520b7a23d
- https://github.com/moodle/moodle/commit/fb2491effb1a7d5d7abb0efba5b3929342990514
- https://github.com/moodle/moodle
- https://moodle.org/mod/forum/discuss.php?d=323237
- http://git.moodle.org/gw?p=moodle.git&a=search&h=HEAD&st=commit&s=MDL-51569
