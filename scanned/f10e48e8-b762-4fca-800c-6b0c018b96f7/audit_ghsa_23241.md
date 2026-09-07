# [M] Moodle XSS Vulnerability

## Summary
Severity: Medium
Advisory: GHSA-4r2p-wpv5-683w
CVE: CVE-2019-3808
CWE: CWE-79
Ecosystem: Packagist
CVSS: CVSS:3.1/AV:N/AC:L/PR:L/UI:R/S:C/C:L/I:L/A:N (CVSS_V3)
Published: 2022-05-13
Source: https://github.com/advisories/GHSA-4r2p-wpv5-683w
Type: github-advisory

## Affected
- Packagist: `moodle/moodle` — affected >=3.6.0 <3.6.2
- Packagist: `moodle/moodle` — affected >=3.5.0 <3.5.4
- Packagist: `moodle/moodle` — affected >=3.2.0 <3.4.7
- Packagist: `moodle/moodle` — affected >=0 <3.1.16

## Details
A flaw was found in Moodle versions 3.6 to 3.6.1, 3.5 to 3.5.3, 3.4 to 3.4.6, 3.1 to 3.1.15 and earlier unsupported versions. The 'manage groups' capability did not have the 'XSS risk' flag assigned to it, but does have that access in certain places. Note that the capability is intended for use by trusted users, and is only assigned to teachers and managers by default.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2019-3808
- https://github.com/moodle/moodle/commit/6360f87cdca744a6a71c315853f6d811a3e54e26
- https://bugzilla.redhat.com/show_bug.cgi?id=CVE-2019-3808
- https://github.com/moodle/moodle
- https://moodle.org/mod/forum/discuss.php?d=381228#p1536765
- http://git.moodle.org/gw?p=moodle.git&a=search&h=HEAD&st=commit&s=MDL-64395
