# [M] Moodle has arbitrary file read risk through pdfTeX

## Summary
Severity: Medium
Advisory: GHSA-vjmm-r9gg-425m
CVE: CVE-2024-43426
CWE: CWE-1287
Ecosystem: Packagist
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:N/A:N (CVSS_V3)
Published: 2024-11-07
Source: https://github.com/advisories/GHSA-vjmm-r9gg-425m
Type: github-advisory

## Affected
- Packagist: `moodle/moodle` — affected >=0 <4.1.12
- Packagist: `moodle/moodle` — affected >=4.2.0-beta <4.2.9
- Packagist: `moodle/moodle` — affected >=4.3.0-beta <4.3.6
- Packagist: `moodle/moodle` — affected >=4.4.0-beta <4.4.2

## Details
A flaw was found in pdfTeX. Insufficient sanitizing in the TeX notation filter resulted in an arbitrary file read risk on sites where pdfTeX is available, such as those with TeX Live installed.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2024-43426
- https://bugzilla.redhat.com/show_bug.cgi?id=2304254
- https://git.moodle.org/gw?p=moodle.git&a=search&h=HEAD&st=commit&s=MDL-82745
- https://github.com/moodle/moodle
- https://moodle.org/mod/forum/discuss.php?d=461194
