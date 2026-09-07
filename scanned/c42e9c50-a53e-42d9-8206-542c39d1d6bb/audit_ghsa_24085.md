# [M] Moodle Allows Modification of Constants

## Summary
Severity: Medium
Advisory: GHSA-jcrj-gmr6-p5j8
CVE: CVE-2011-4301
CWE: CWE-471
Ecosystem: Packagist
Published: 2022-05-13
Source: https://github.com/advisories/GHSA-jcrj-gmr6-p5j8
Type: github-advisory

## Affected
- Packagist: `moodle/moodle` — affected >=0 <1.9.14
- Packagist: `moodle/moodle` — affected >=2.0 <2.0.5
- Packagist: `moodle/moodle` — affected >=2.1 <2.1.2

## Details
The `MoodleQuickForm` class in the Forms Library in `lib/formslib.php` in Moodle 1.9.x before 1.9.14, 2.0.x before 2.0.5, and 2.1.x before 2.1.2 does not recognize Forms API `setConstant` operations, which allows remote attackers to submit unexpected form content by modifying the values of constant fields.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2011-4301
- https://github.com/moodle/moodle/commit/1f52e72526c305989eadc702b5299edb2a50ac3c
- https://github.com/moodle/moodle/commit/2a44c5192c875c4f4b4e813d7227b19d8fda86ba
- https://github.com/moodle/moodle/commit/a6f18c98f43b6fc6b8b7c4e96af41cb4a626e1b8
- https://github.com/moodle/moodle/commit/f1f70bd4dde6cd1ea4bdb8ab28fa3d36a53b89d8
- https://bugzilla.redhat.com/show_bug.cgi?id=747444
- https://github.com/moodle/moodle
- http://git.moodle.org/gw?p=moodle.git%3Ba=commit%3Bh=f1f70bd4dde6cd1ea4bdb8ab28fa3d36a53b89d8
- http://git.moodle.org/gw?p=moodle.git;a=commit;h=f1f70bd4dde6cd1ea4bdb8ab28fa3d36a53b89d8
- http://moodle.org/mod/forum/discuss.php?d=188313
