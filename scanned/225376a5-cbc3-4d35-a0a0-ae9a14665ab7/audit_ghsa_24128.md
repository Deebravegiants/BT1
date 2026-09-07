# [M] Moodle allows attackers to delete files

## Summary
Severity: Medium
Advisory: GHSA-44xp-wj24-9xxj
CVE: CVE-2015-5265
Ecosystem: Packagist
CVSS: CVSS:3.0/AV:N/AC:L/PR:L/UI:N/S:U/C:N/I:L/A:N (CVSS_V3)
Published: 2022-05-13
Source: https://github.com/advisories/GHSA-44xp-wj24-9xxj
Type: github-advisory

## Affected
- Packagist: `moodle/moodle` — affected >=2.7.0 <2.7.10
- Packagist: `moodle/moodle` — affected >=2.8.0 <2.8.8
- Packagist: `moodle/moodle` — affected >=2.9.0 <2.9.2

## Details
The wiki component in Moodle through 2.6.11, 2.7.x before 2.7.10, 2.8.x before 2.8.8, and 2.9.x before 2.9.2 does not consider the mod/wiki:managefiles capability before authorizing file management, which allows remote authenticated users to delete arbitrary files by using a manage-files button in a text editor.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2015-5265
- https://github.com/moodle/moodle/commit/037e05e8b266bff4835f0d2eea33ef86fb71d585
- https://github.com/moodle/moodle/commit/1d70050f33edb79b974de2509f18c943969589ea
- https://github.com/moodle/moodle/commit/40a154551fcdf0b9ea906f4d1313df29754f1fa1
- https://github.com/moodle/moodle/commit/78de2e86e8506222cf49b1cc6dc58467750ae83d
- https://github.com/moodle/moodle
- https://moodle.org/mod/forum/discuss.php?d=320289
- https://web.archive.org/web/20160323063809/http://www.securitytracker.com/id/1033619
- http://git.moodle.org/gw?p=moodle.git&a=search&h=HEAD&st=commit&s=MDL-48371
- http://www.openwall.com/lists/oss-security/2015/09/21/1
