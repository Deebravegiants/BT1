# [M] Moodle External function mod_assign_save_submission does not check due dates

## Summary
Severity: Medium
Advisory: GHSA-cw72-69wq-f9f2
CVE: CVE-2016-2159
CWE: CWE-284
Ecosystem: Packagist
CVSS: CVSS:3.0/AV:N/AC:L/PR:L/UI:N/S:U/C:N/I:L/A:N (CVSS_V3)
Published: 2022-05-13
Source: https://github.com/advisories/GHSA-cw72-69wq-f9f2
Type: github-advisory

## Affected
- Packagist: `moodle/moodle` — affected >=2.7 <2.7.13
- Packagist: `moodle/moodle` — affected >=2.8 <2.8.11
- Packagist: `moodle/moodle` — affected >=2.9 <2.9.5
- Packagist: `moodle/moodle` — affected >=3.0 <3.0.3

## Details
The save_submission function in mod/assign/externallib.php in Moodle through 2.6.11, 2.7.x before 2.7.13, 2.8.x before 2.8.11, 2.9.x before 2.9.5, and 3.0.x before 3.0.3 allows remote authenticated users to bypass intended due-date restrictions by leveraging the student role for a web-service request.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2016-2159
- https://github.com/moodle/moodle/commit/0766509ab02353008af62f953f7ebc0f6210411a
- https://github.com/moodle/moodle/commit/3c069c16db62d0e0a64137578e92c22d604dd261
- https://github.com/moodle/moodle/commit/711f9468d4e2792afe0f2025ac98c52ee3e4ee71
- https://github.com/moodle/moodle/commit/dc8421575f35585a7a4fc1c9710dafd1d0483d4e
- https://github.com/moodle/moodle/commit/ea8987644fdbbee291337263598b0c3c7bf27c36
- https://github.com/moodle/moodle
- https://moodle.org/mod/forum/discuss.php?d=330182
- https://web.archive.org/web/20160424224349/http://www.securitytracker.com/id/1035333
- http://git.moodle.org/gw?p=moodle.git&a=search&h=HEAD&st=commit&s=MDL-52901
- http://www.openwall.com/lists/oss-security/2016/03/21/1
