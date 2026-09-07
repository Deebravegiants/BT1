# [M] Moodle does not verify group permissions

## Summary
Severity: Medium
Advisory: GHSA-557f-2hv4-7jjm
CVE: CVE-2014-7834
Ecosystem: Packagist
Published: 2022-05-13
Source: https://github.com/advisories/GHSA-557f-2hv4-7jjm
Type: github-advisory

## Affected
- Packagist: `moodle/moodle` — affected >=2.6.0 <2.6.6
- Packagist: `moodle/moodle` — affected >=2.7.0 <2.7.3

## Details
mod/forum/externallib.php in Moodle 2.6.x before 2.6.6 and 2.7.x before 2.7.3 does not verify group permissions, which allows remote authenticated users to access a forum via the forum_get_discussions web service.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2014-7834
- https://github.com/moodle/moodle/commit/3aa9d93c7a78d14fa30e2afbfd8fa7e09bc9cb41
- https://github.com/moodle/moodle/commit/40afeb4044c9718bf175c347f0f9099a037ce9f0
- https://github.com/moodle/moodle/commit/79eda0e9a0d15ba1d87187ec712f96abd62748c1
- https://github.com/moodle/moodle
- https://moodle.org/mod/forum/discuss.php?d=275159
- https://web.archive.org/web/20150914064838/http://www.securitytracker.com/id/1031215
- http://git.moodle.org/gw?p=moodle.git&a=search&h=HEAD&st=commit&s=MDL-45303
- http://openwall.com/lists/oss-security/2014/11/17/11
