# [H] MantisBT Insufficient Session Expiration cookie string not reset after logout

## Summary
Severity: High
Advisory: GHSA-jm72-67rm-763j
CVE: CVE-2009-20001
CWE: CWE-613
Ecosystem: Packagist
CVSS: CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:N (CVSS_V3)
Published: 2022-04-21
Source: https://github.com/advisories/GHSA-jm72-67rm-763j
Type: github-advisory

## Affected
- Packagist: `mantisbt/mantisbt` — affected >=0 <2.24.5

## Details
An issue was discovered in MantisBT before 2.24.5. It associates a unique cookie string with each user. This string is not reset upon logout (i.e., the user session is still considered valid and active), allowing an attacker who somehow gained access to a user's cookie to login as them.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2009-20001
- https://github.com/mantisbt/mantisbt/commit/79a78c09d5ef5ce098adc73f6f1416f00fc238a5
- https://github.com/mantisbt/mantisbt
- https://mantisbt.org/bugs/view.php?id=11296
- https://mantisbt.org/bugs/view.php?id=27976
