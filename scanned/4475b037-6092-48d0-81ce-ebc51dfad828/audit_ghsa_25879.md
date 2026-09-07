# [H] SQL Injection in Moodle

## Summary
Severity: High
Advisory: GHSA-h2fw-93qx-vrcq
CVE: CVE-2022-0983
CWE: CWE-89
Ecosystem: Packagist
CVSS: CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H (CVSS_V3)
Published: 2022-03-26
Source: https://github.com/advisories/GHSA-h2fw-93qx-vrcq
Type: github-advisory

## Affected
- Packagist: `moodle/moodle` — affected >=3.11.0 <3.11.6
- Packagist: `moodle/moodle` — affected >=3.10.0 <3.10.10
- Packagist: `moodle/moodle` — affected >=0 <3.9.13

## Details
An SQL injection risk was identified in Badges code relating to configuring criteria. Access to the relevant capability was limited to teachers and managers by default.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2022-0983
- https://github.com/moodle/moodle/commit/c2794752ea3cdda2d64a0651da08b2cdf730d9f1
- https://bugzilla.redhat.com/show_bug.cgi?id=2064119
- https://git.moodle.org/gw?p=moodle.git&a=search&h=HEAD&st=commit&s=MDL-74074
- https://github.com/moodle/moodle
- https://lists.fedoraproject.org/archives/list/package-announce@lists.fedoraproject.org/message/G4GRMWBGHOJMFXMTORECQNULJK7ZJJ6Y
