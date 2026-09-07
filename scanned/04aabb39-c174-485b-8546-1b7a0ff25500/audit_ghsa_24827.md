# [M] Moodle XSS Vulnerability

## Summary
Severity: Medium
Advisory: GHSA-r729-mx2r-j26j
CVE: CVE-2011-4306
CWE: CWE-79
Ecosystem: Packagist
Published: 2022-05-13
Source: https://github.com/advisories/GHSA-r729-mx2r-j26j
Type: github-advisory

## Affected
- Packagist: `moodle/moodle` — affected >=0 <1.9.14

## Details
Cross-site scripting (XSS) vulnerability in `course/editsection.html` in Moodle 1.9.x before 1.9.14 allows remote authenticated users to inject arbitrary web script or HTML via crafted data.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2011-4306
- https://github.com/moodle/moodle/commit/4a2acd8c7e6c869d5fd5aa686e6e0a3f20c97f15
- https://bugzilla.redhat.com/show_bug.cgi?id=747444
- http://git.moodle.org/gw?p=moodle.git%3Ba=commit%3Bh=4a2acd8c7e6c869d5fd5aa686e6e0a3f20c97f15
- http://git.moodle.org/gw?p=moodle.git;a=commit;h=4a2acd8c7e6c869d5fd5aa686e6e0a3f20c97f15
- http://moodle.org/mod/forum/discuss.php?d=188319
