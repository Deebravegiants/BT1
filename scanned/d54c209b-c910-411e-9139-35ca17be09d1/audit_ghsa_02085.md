# [M] ckeditor4 vulnerable to cross-site scripting

## Summary
Severity: Medium
Advisory: GHSA-rgx6-rjj4-c388
CVE: CVE-2021-33829
CWE: CWE-79
Ecosystem: Packagist, npm
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:R/S:C/C:L/I:L/A:N (CVSS_V3)
Published: 2021-06-21
Source: https://github.com/advisories/GHSA-rgx6-rjj4-c388
Type: github-advisory

## Affected
- npm: `ckeditor4` — affected >=4.14.0 <4.16.1
- Packagist: `drupal/core` — affected >=7.0.0 <7.80
- Packagist: `drupal/core` — affected >=8.0.0 <8.9.16
- Packagist: `drupal/core` — affected >=9.0.0 <9.0.14
- Packagist: `drupal/core` — affected >=9.1.0 <9.1.9
- Packagist: `drupal/drupal` — affected >=7.0.0 <7.80
- Packagist: `drupal/drupal` — affected >=8.0.0 <8.9.16
- Packagist: `drupal/drupal` — affected >=9.0.0 <9.0.14
- Packagist: `drupal/drupal` — affected >=9.1.0 <9.1.9

## Details
A cross-site scripting (XSS) vulnerability in the HTML Data Processor in CKEditor 4 4.14.0 through 4.16.x before 4.16.1 allows remote attackers to inject executable JavaScript code through a crafted comment because `--!>` is mishandled.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2021-33829
- https://ckeditor.com/blog/ckeditor-4.16.1-with-accessibility-enhancements/#improvements-for-comments-in-html-parser
- https://github.com/FriendsOfPHP/security-advisories/blob/master/drupal/core/CVE-2021-33829.yaml
- https://github.com/FriendsOfPHP/security-advisories/blob/master/drupal/drupal/CVE-2021-33829.yaml
- https://github.com/ckeditor/ckeditor4
- https://lists.debian.org/debian-lts-announce/2021/11/msg00007.html
- https://lists.fedoraproject.org/archives/list/package-announce@lists.fedoraproject.org/message/NYA354LJP47KCVJMTUO77ZCX3ZK42G3T
- https://lists.fedoraproject.org/archives/list/package-announce@lists.fedoraproject.org/message/UVOYN2WKDPLKCNILIGEZM236ABQASLGW
- https://lists.fedoraproject.org/archives/list/package-announce@lists.fedoraproject.org/message/WAGNWHFIQAVCP537KFFS2A2GDG66J7XD
- https://www.drupal.org/sa-core-2021-003
- https://www.npmjs.com/package/ckeditor4
