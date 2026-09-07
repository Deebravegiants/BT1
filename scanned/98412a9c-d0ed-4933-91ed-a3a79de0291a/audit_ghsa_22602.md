# [M] Moodle allows attackers to discover hidden course names

## Summary
Severity: Medium
Advisory: GHSA-fmq9-58q4-xjw5
CVE: CVE-2016-2154
CWE: CWE-200
Ecosystem: Packagist
CVSS: CVSS:3.0/AV:N/AC:L/PR:L/UI:N/S:U/C:L/I:N/A:N (CVSS_V3)
Published: 2022-05-13
Source: https://github.com/advisories/GHSA-fmq9-58q4-xjw5
Type: github-advisory

## Affected
- Packagist: `moodle/moodle` — affected >=2.8.0 <2.8.11
- Packagist: `moodle/moodle` — affected >=2.9.0 <2.9.5
- Packagist: `moodle/moodle` — affected >=3.0.0 <3.0.3

## Details
admin/tool/monitor/lib.php in Event Monitor in Moodle 2.8.x before 2.8.11, 2.9.x before 2.9.5, and 3.0.x before 3.0.3 does not consider the moodle/course:viewhiddencourses capability, which allows remote authenticated users to discover hidden course names by subscribing to a rule.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2016-2154
- https://github.com/moodle/moodle/commit/214950de2a4149f0efeabf62b0978901c1c68015
- https://github.com/moodle/moodle/commit/406a0efd3720d3b9214508b2e47b8f4401061312
- https://github.com/moodle/moodle/commit/475362630ba4c5073a05b1c81caf3a7f3f373cd1
- https://github.com/moodle/moodle/commit/4e5732e7fe0e9363618039d434cb5b774a8772b0
- https://github.com/moodle/moodle/commit/89b97390d0bedd2567d61723f76caa222026d5fb
- https://github.com/moodle/moodle/commit/ff7bacf32bbe148a7ab6db3b5fa69e106e54d6a4
- https://github.com/moodle/moodle
- https://moodle.org/mod/forum/discuss.php?d=330176
- https://web.archive.org/web/20160424224349/http://www.securitytracker.com/id/1035333
- http://git.moodle.org/gw?p=moodle.git&a=search&h=HEAD&st=commit&s=MDL-51167
- http://www.openwall.com/lists/oss-security/2016/03/21/1
