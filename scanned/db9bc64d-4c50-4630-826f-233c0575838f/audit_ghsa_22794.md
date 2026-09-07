# [H] Moodle calculated question type allows remote code execution by Question authors

## Summary
Severity: High
Advisory: GHSA-xh2j-q4mc-v522
CVE: CVE-2018-1133
CWE: CWE-94
Ecosystem: Packagist
CVSS: CVSS:3.0/AV:N/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H (CVSS_V3)
Published: 2022-05-13
Source: https://github.com/advisories/GHSA-xh2j-q4mc-v522
Type: github-advisory

## Affected
- Packagist: `moodle/moodle` — affected >=3.1 <3.1.12
- Packagist: `moodle/moodle` — affected >=3.2 <3.2.9
- Packagist: `moodle/moodle` — affected >=3.3 <3.3.6
- Packagist: `moodle/moodle` — affected >=3.4 <3.4.3

## Details
An issue was discovered in Moodle 3.x. A Teacher creating a Calculated question can intentionally cause remote code execution on the server, aka eval injection.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2018-1133
- https://github.com/moodle/moodle
- https://moodle.org/mod/forum/discuss.php?d=371199
- https://www.exploit-db.com/exploits/46551
- http://www.securityfocus.com/bid/104307
