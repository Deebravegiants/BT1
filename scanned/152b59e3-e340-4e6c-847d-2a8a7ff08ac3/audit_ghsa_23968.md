# [M] Moodle allows attackers obtain full-name information

## Summary
Severity: Medium
Advisory: GHSA-fqrg-vmvj-jv3x
CVE: CVE-2015-3176
CWE: CWE-200
Ecosystem: Packagist
Published: 2022-05-13
Source: https://github.com/advisories/GHSA-fqrg-vmvj-jv3x
Type: github-advisory

## Affected
- Packagist: `moodle/moodle` — affected >=0 <2.6.11
- Packagist: `moodle/moodle` — affected >=2.7.0 <2.7.8
- Packagist: `moodle/moodle` — affected >=2.8.0 <2.8.6

## Details
The account-confirmation feature in login/confirm.php in Moodle through 2.5.9, 2.6.x before 2.6.11, 2.7.x before 2.7.8, and 2.8.x before 2.8.6 allows remote attackers to obtain sensitive full-name information by attempting to self-register.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2015-3176
- https://github.com/moodle/moodle/commit/4f8b6d567494375017c4bc2228e1668d13b21645
- https://github.com/moodle/moodle/commit/80eb5bc7b7da4927d2d8021e8c18cbd3a8093406
- https://github.com/moodle/moodle/commit/d5922686e7622e1aa58b9b31633f0906f5be2eb3
- https://github.com/moodle/moodle/commit/e2e7e35da31ef174589d54f70e791d6acefb59c9
- https://github.com/moodle/moodle
- https://moodle.org/mod/forum/discuss.php?d=313683
- https://web.archive.org/web/20200228054912/http://www.securityfocus.com/bid/74644
- https://web.archive.org/web/20201030042703/http://www.securitytracker.com/id/1032358
- http://git.moodle.org/gw?p=moodle.git&a=search&h=HEAD&st=commit&s=MDL-50099
- http://openwall.com/lists/oss-security/2015/05/18/1
