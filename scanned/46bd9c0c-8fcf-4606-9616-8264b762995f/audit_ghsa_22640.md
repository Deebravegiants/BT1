# [M] Moodle multiple cross-site request forgery (CSRF) vulnerabilities

## Summary
Severity: Medium
Advisory: GHSA-wpq5-q3mj-8f3r
CVE: CVE-2014-7836
CWE: CWE-352
Ecosystem: Packagist
Published: 2022-05-13
Source: https://github.com/advisories/GHSA-wpq5-q3mj-8f3r
Type: github-advisory

## Affected
- Packagist: `moodle/moodle` — affected >=0 <2.5.9
- Packagist: `moodle/moodle` — affected >=2.6.0 <2.6.6
- Packagist: `moodle/moodle` — affected >=2.7.0 <2.7.3

## Details
Multiple cross-site request forgery (CSRF) vulnerabilities in the LTI module in Moodle through 2.4.11, 2.5.x before 2.5.9, 2.6.x before 2.6.6, and 2.7.x before 2.7.3 allow remote attackers to hijack the authentication of arbitrary users for a (1) mod/lti/request_tool.php or (2) mod/lti/instructor_edit_tool_type.php request.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2014-7836
- https://github.com/moodle/moodle/commit/48ea41c48f3dcf28fb40fe0b0a1f0c4c0453d34d
- https://github.com/moodle/moodle/commit/75d7e25198eeb6255963e2e46212d89b14e05dd7
- https://github.com/moodle/moodle/commit/babaf596e10ee525e58314b36f8063c65b59aa7d
- https://github.com/moodle/moodle/commit/bac38b11ab95862a831c6e6e60c03caf64eda599
- https://github.com/moodle/moodle
- https://moodle.org/mod/forum/discuss.php?d=275162
- https://web.archive.org/web/20150914064838/http://www.securitytracker.com/id/1031215
- http://git.moodle.org/gw?p=moodle.git&a=search&h=HEAD&st=commit&s=MDL-47924
- http://openwall.com/lists/oss-security/2014/11/17/11
