# [M] PHP Spellchecker addon for TinyMCE allows attackers to trigger arbitrary outbound HTTP requests

## Summary
Severity: Medium
Advisory: GHSA-fx5h-3786-h2w6
CVE: CVE-2012-6112
Ecosystem: Packagist
Published: 2022-05-13
Source: https://github.com/advisories/GHSA-fx5h-3786-h2w6
Type: github-advisory

## Affected
- Packagist: `moodle/moodle` — affected >=2.1.0 <2.1.10
- Packagist: `moodle/moodle` — affected >=2.2.0 <2.2.7
- Packagist: `moodle/moodle` — affected >=2.3.0 <2.3.4
- Packagist: `moodle/moodle` — affected >=2.4.0 <2.4.1

## Details
classes/GoogleSpell.php in the PHP Spellchecker (aka Google Spellchecker) addon before 2.0.6.1 for TinyMCE, as used in Moodle 2.1.x before 2.1.10, 2.2.x before 2.2.7, 2.3.x before 2.3.4, and 2.4.x before 2.4.1 and other products, does not properly handle control characters, which allows remote attackers to trigger arbitrary outbound HTTP requests via a crafted string.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2012-6112
- https://github.com/moodle/moodle/commit/6fac8f7f04c9fe7f8bbb54a9c00ec5f9ea4f09e0
- https://github.com/moodle/moodle/commit/9803d8fc3ce08c8f8b88ad3a95d9a7c97678a3e3
- https://github.com/moodle/moodle/commit/a3243760c243ddad76e91840134009c3681cb16a
- https://github.com/moodle/moodle/commit/f938b1a89b8f381129120a37915d1b345333b3fb
- https://github.com/tinymce/tinymce_spellchecker_php/commit/22910187bfb9edae90c26e10100d8145b505b974
- https://github.com/moodle/moodle
- https://moodle.org/mod/forum/discuss.php?d=220157
- https://web.archive.org/web/20121015010345/http://www.tinymce.com/develop/changelog/?type=phpspell
- https://web.archive.org/web/20121129021911/http://www.tinymce.com/forum/viewtopic.php?id=30036
- http://git.moodle.org/gw?p=moodle.git&a=search&h=HEAD&st=commit&s=MDL-37283
- http://openwall.com/lists/oss-security/2013/01/21/1
