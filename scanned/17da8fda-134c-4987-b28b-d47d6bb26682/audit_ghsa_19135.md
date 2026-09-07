# [M] Moodle's non-searchable tags can still be discovered on the tag search page and in the tags block

## Summary
Severity: Medium
Advisory: GHSA-5r85-6h7f-rg3r
CVE: CVE-2025-26527
CWE: CWE-1230
Ecosystem: Packagist
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:L/I:N/A:N (CVSS_V3)
Published: 2025-02-24
Source: https://github.com/advisories/GHSA-5r85-6h7f-rg3r
Type: github-advisory

## Affected
- Packagist: `moodle/moodle` — affected >=4.5.0-beta <4.5.2
- Packagist: `moodle/moodle` — affected >=4.4.0-beta <4.4.6
- Packagist: `moodle/moodle` — affected >=4.3.0-beta <4.3.10
- Packagist: `moodle/moodle` — affected >=0 <4.1.16

## Details
Tags not expected to be visible to a user could still be discovered by them via the tag search page or in the tags block.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2025-26527
- https://github.com/moodle/moodle
- https://moodle.org/mod/forum/discuss.php?d=466143
- http://git.moodle.org/gw?p=moodle.git&a=search&h=HEAD&st=commit&s=MDL-83941
