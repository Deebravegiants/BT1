# [M] Moodle allows attackers to extract archives to arbitrary directories

## Summary
Severity: Medium
Advisory: GHSA-cm4r-58pj-h2ph
CVE: CVE-2015-2267
CWE: CWE-284
Ecosystem: Packagist
Published: 2022-05-13
Source: https://github.com/advisories/GHSA-cm4r-58pj-h2ph
Type: github-advisory

## Affected
- Packagist: `moodle/moodle` — affected >=0 <2.6.9
- Packagist: `moodle/moodle` — affected >=2.7.0 <2.7.6
- Packagist: `moodle/moodle` — affected >=2.8.0 <2.8.4

## Details
mdeploy.php in Moodle through 2.5.9, 2.6.x before 2.6.9, 2.7.x before 2.7.6, and 2.8.x before 2.8.4 allows remote authenticated users to bypass intended access restrictions and extract archives to arbitrary directories via a crafted dataroot value.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2015-2267
- https://github.com/moodle/moodle/commit/12a8fcb5e45c58ee8267ad0472852c2b80a19878
- https://github.com/moodle/moodle/commit/240e7be7341afa31096fdbf3f242a7966f6237ab
- https://github.com/moodle/moodle/commit/4475f1e478370fb97933127ec60e40f39e285da1
- https://github.com/moodle/moodle/commit/76da7e9bc88669eab62f83f04639ba356a0b0c5a
- https://github.com/moodle/moodle/commit/83866c3c2a5b1391317172eea0b4f017c6d142d2
- https://github.com/moodle/moodle/commit/84f9f60b67e1e20058fbe2afa473607d075aff63
- https://github.com/moodle/moodle/commit/8d9bdd28e049ca6b6b2a4ab8f142097c2f907df6
- https://github.com/moodle/moodle/commit/a47aabc7833d0c88a83791d99a1204742c33f59b
- https://github.com/moodle/moodle/commit/c353a6202658f320096a41e94494063393153b7f
- https://github.com/moodle/moodle/commit/de169b7944e36d374d55e3f396d90ab2b4303afb
- https://github.com/moodle/moodle
- https://moodle.org/mod/forum/discuss.php?d=307381
- http://git.moodle.org/gw?p=moodle.git&a=search&h=HEAD&st=commit&s=MDL-49087
- http://openwall.com/lists/oss-security/2015/03/16/1
