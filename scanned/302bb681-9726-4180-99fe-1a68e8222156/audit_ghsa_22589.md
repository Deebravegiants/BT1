# [C] Incorrect Calculation in moodle

## Summary
Severity: Critical
Advisory: GHSA-w37f-pvvx-wcwm
CVE: CVE-2022-30600
CWE: CWE-682
Ecosystem: Packagist
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H (CVSS_V3)
Published: 2022-05-19
Source: https://github.com/advisories/GHSA-w37f-pvvx-wcwm
Type: github-advisory

## Affected
- Packagist: `moodle/moodle` — affected >=4.0 <4.0.1
- Packagist: `moodle/moodle` — affected >=3.9 <3.9.14
- Packagist: `moodle/moodle` — affected >=3.10 <3.10.11
- Packagist: `moodle/moodle` — affected >=3.11 <3.11.7

## Details
A flaw was found in moodle where logic used to count failed login attempts could result in the account lockout threshold being bypassed.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2022-30600
- https://github.com/moodle/moodle/commit/59b5858da200f63ecb59a9113af2b99ef1496fe5
- https://bugzilla.redhat.com/show_bug.cgi?id=2083613
- https://github.com/moodle/moodle
- https://lists.fedoraproject.org/archives/list/package-announce@lists.fedoraproject.org/message/OGF35EN5K2R6X3NTY3XPZSJ3UDASMXI6
- https://lists.fedoraproject.org/archives/list/package-announce@lists.fedoraproject.org/message/PIMSIRKCFLIC646K4GMUSZU7THOUVPAJ
- https://lists.fedoraproject.org/archives/list/package-announce@lists.fedoraproject.org/message/QCTWSE3JDMSYL7DPCMXMMJEXZSS6VIA5
- https://moodle.org/mod/forum/discuss.php?d=434582
- http://git.moodle.org/gw?p=moodle.git&a=search&h=HEAD&st=commit&s=MDL-73736
