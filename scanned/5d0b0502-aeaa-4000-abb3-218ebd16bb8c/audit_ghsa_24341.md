# [M] Moodle does not enforce the moodle/site:accessallgroups capability requirement

## Summary
Severity: Medium
Advisory: GHSA-mg69-5q59-8jcg
CVE: CVE-2014-3553
Ecosystem: Packagist
Published: 2022-05-13
Source: https://github.com/advisories/GHSA-mg69-5q59-8jcg
Type: github-advisory

## Affected
- Packagist: `moodle/moodle` — affected >=0 <2.5.7
- Packagist: `moodle/moodle` — affected >=2.6.0 <2.6.4
- Packagist: `moodle/moodle` — affected >=2.7.0 <2.7.1

## Details
mod/forum/classes/post_form.php in Moodle through 2.3.11, 2.4.x before 2.4.11, 2.5.x before 2.5.7, 2.6.x before 2.6.4, and 2.7.x before 2.7.1 does not enforce the moodle/site:accessallgroups capability requirement before proceeding with a post to all groups, which allows remote authenticated users to bypass intended access restrictions by leveraging two or more group memberships.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2014-3553
- https://github.com/moodle/moodle/commit/5c74e0daca748ffbbbf17a410abd8c85335b2116
- https://github.com/moodle/moodle/commit/91c8d4da71a6706c70071f9182e8ae6110c86d70
- https://github.com/moodle/moodle/commit/e3fd900dcda7b603d7e0749008abd0d01290bbc3
- https://github.com/moodle/moodle/commit/f2946a5419a94f19cb3490a249fe0bb50161f254
- https://github.com/moodle/moodle
- https://moodle.org/mod/forum/discuss.php?d=264268
- http://git.moodle.org/gw?p=moodle.git&a=search&h=HEAD&st=commit&s=MDL-38990
- http://openwall.com/lists/oss-security/2014/07/21/1
