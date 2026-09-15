# [M] Ouch Improper Restriction of Operations within the Bounds of a Memory Buffer vulnerability

## Summary
Severity: Medium
Advisory: GHSA-6xfj-hhwh-r3c2
CVE: CVE-2024-13941
CWE: CWE-119
Ecosystem: crates.io
CVSS: CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:L/I:L/A:L (CVSS_V3)
Published: 2025-04-01
Source: https://github.com/advisories/GHSA-6xfj-hhwh-r3c2
Type: github-advisory

## Affected
- crates.io: `ouch` — affected >=0 <0.4.0

## Details
A vulnerability was found in ouch-org ouch up to 0.3.1. It has been classified as critical. This affects the function ouch::archive::zip::convert_zip_date_time of the file zip.rs. The manipulation of the argument month leads to memory corruption. The attack needs to be approached locally. The exploit has been disclosed to the public and may be used. Upgrading to version 0.4.0 is able to address this issue. It is recommended to upgrade the affected component.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2024-13941
- https://github.com/ouch-org/ouch/issues/707
- https://github.com/rustsec/advisory-db/pull/2084/files
- https://github.com/ouch-org/ouch
- https://github.com/ouch-org/ouch/releases/tag/0.4.0
- https://github.com/user-attachments/files/16767988/ouch.crash.report.docx
- https://vuldb.com/?ctiid.302055
- https://vuldb.com/?id.302055
- https://vuldb.com/?submit.524511
