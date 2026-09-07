# [M] Moodle does not consider the moodle/tag:edit capability before adding a tag

## Summary
Severity: Medium
Advisory: GHSA-468q-9cmp-76wc
CVE: CVE-2014-7846
Ecosystem: Packagist
Published: 2022-05-13
Source: https://github.com/advisories/GHSA-468q-9cmp-76wc
Type: github-advisory

## Affected
- Packagist: `moodle/moodle` — affected >=0 <2.5.9
- Packagist: `moodle/moodle` — affected >=2.6.0 <2.6.6
- Packagist: `moodle/moodle` — affected >=2.7.0 <2.7.3

## Details
tag/tag_autocomplete.php in Moodle through 2.4.11, 2.5.x before 2.5.9, 2.6.x before 2.6.6, and 2.7.x before 2.7.3 does not consider the moodle/tag:edit capability before adding a tag, which allows remote authenticated users to bypass intended access restrictions via an AJAX request.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2014-7846
- https://github.com/moodle/moodle/commit/1d9e0857f8bd9f21d25886f77cc13120f9d6be08
- https://github.com/moodle/moodle/commit/932694ca59413ce8a0546b8bfb97e07e3b4cf17b
- https://github.com/moodle/moodle/commit/bb69623c5c0754467f01f916f94446e1caddb6a8
- https://github.com/moodle/moodle
- https://moodle.org/mod/forum/discuss.php?d=275157
- https://web.archive.org/web/20150914064838/http://www.securitytracker.com/id/1031215
- http://git.moodle.org/gw?p=moodle.git&a=search&h=HEAD&st=commit&s=MDL-47965
- http://openwall.com/lists/oss-security/2014/11/17/11
