# [M] Exposure of Sensitive Information in moodle

## Summary
Severity: Medium
Advisory: GHSA-fj6p-g234-rrv3
CVE: CVE-2022-30598
CWE: CWE-200
Ecosystem: Packagist
CVSS: CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:L/I:N/A:N (CVSS_V3)
Published: 2022-05-19
Source: https://github.com/advisories/GHSA-fj6p-g234-rrv3
Type: github-advisory

## Affected
- Packagist: `moodle/moodle` — affected >=4.0 <4.0.1
- Packagist: `moodle/moodle` — affected >=3.11 <3.11.7
- Packagist: `moodle/moodle` — affected >=3.10 <3.10.11
- Packagist: `moodle/moodle` — affected >=3.9 <3.9.14

## Details
A flaw was found in moodle where global search results could include author information on some activities where a user may not otherwise have access to it.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2022-30598
- https://github.com/moodle/moodle/commit/4f2eac208d8af4a833f81364e39a5579f39642b1
- https://bugzilla.redhat.com/show_bug.cgi?id=2083592
- https://github.com/moodle/moodle
- https://lists.fedoraproject.org/archives/list/package-announce@lists.fedoraproject.org/message/OGF35EN5K2R6X3NTY3XPZSJ3UDASMXI6
- https://lists.fedoraproject.org/archives/list/package-announce@lists.fedoraproject.org/message/PIMSIRKCFLIC646K4GMUSZU7THOUVPAJ
- https://lists.fedoraproject.org/archives/list/package-announce@lists.fedoraproject.org/message/QCTWSE3JDMSYL7DPCMXMMJEXZSS6VIA5
- https://moodle.org/mod/forum/discuss.php?d=434580
- http://git.moodle.org/gw?p=moodle.git&a=search&h=HEAD&st=commit&s=MDL-71623
