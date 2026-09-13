# [H] JasperReports has a Java deserialisation vulnerability

## Summary
Severity: High
Advisory: GHSA-7c3f-cg9x-f3gr
CVE: CVE-2025-10492
CWE: CWE-502
Ecosystem: Maven
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H (CVSS_V3)
Published: 2025-09-16
Source: https://github.com/advisories/GHSA-7c3f-cg9x-f3gr
Type: github-advisory

## Affected
- Maven: `net.sf.jasperreports:jasperreports` — affected >=0 <7.0.4

## Details
A Java deserialisation vulnerability has been discovered in the Jaspersoft Library. Improper handling of externally supplied data may allow attackers to execute arbitrary code remotely on systems that use the affected library.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2025-10492
- https://github.com/Jaspersoft/jasperreports/issues/542
- https://github.com/Jaspersoft/jasperreports/commit/3541a3e2b1ad8b78388ac505091da75cb652a647
- https://github.com/Jaspersoft/jasperreports/commit/827c2f27c4ca8e2c5b3142d76df9c1c8575f3569
- https://community.jaspersoft.com/advisories/jaspersoft-security-advisory-september-16-2025-jaspersoft-library-cve-2025-10492-r6
- https://community.jaspersoft.com/forums/topic/69926-cve-2025-10492-%E2%80%93-no-fix-available-after-jasperreports-upgrade-community-edition
- https://github.com/Jaspersoft/jasperreports
