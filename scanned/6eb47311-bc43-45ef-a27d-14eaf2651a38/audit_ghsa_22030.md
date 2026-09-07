# [M] Moodle context freezing

## Summary
Severity: Medium
Advisory: GHSA-v2rh-5v88-rgvh
CVE: CVE-2019-3852
Ecosystem: Packagist
CVSS: CVSS:3.0/AV:N/AC:L/PR:L/UI:N/S:U/C:N/I:L/A:N (CVSS_V3)
Published: 2022-05-13
Source: https://github.com/advisories/GHSA-v2rh-5v88-rgvh
Type: github-advisory

## Affected
- Packagist: `moodle/moodle` — affected >=3.6 <3.6.3

## Details
A vulnerability was found in moodle before version 3.6.3. The get_with_capability_join and get_users_by_capability functions were not taking context freezing into account when checking user capabilities

## References
- https://nvd.nist.gov/vuln/detail/CVE-2019-3852
- https://github.com/moodle/moodle/commit/5ee3cbc624c1c4d39adc08c2121a1738d6b5e700
- https://github.com/moodle/moodle/commit/90c2e5e707c27cd1ef0b992cc5e55e76dcd17204
- https://bugzilla.redhat.com/show_bug.cgi?id=CVE-2019-3852
- https://github.com/moodle/moodle
- https://moodle.org/mod/forum/discuss.php?d=384015#p1547748
- https://web.archive.org/web/20210624085935/http://git.moodle.org/gw?p=moodle.git&a=search&h=HEAD&st=commit&s=MDL-64410
