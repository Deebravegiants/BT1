# [M] ShifuML shifu code injection vulnerability

## Summary
Severity: Medium
Advisory: GHSA-5fpq-3c9p-3r3w
CVE: CVE-2023-7148
CWE: CWE-94
Ecosystem: Maven
CVSS: CVSS:3.1/AV:N/AC:H/PR:N/UI:R/S:U/C:L/I:L/A:L (CVSS_V3)
Published: 2023-12-29
Source: https://github.com/advisories/GHSA-5fpq-3c9p-3r3w
Type: github-advisory

## Affected
- Maven: `ml.shifu:shifu` — affected >=0

## Details
A vulnerability has been found in ShifuML shifu 0.12.0 and classified as critical. Affected by this vulnerability is an unknown functionality of the file src/main/java/ml/shifu/shifu/core/DataPurifier.java of the component Java Expression Language Handler. The manipulation of the argument FilterExpression leads to code injection. The attack can be launched remotely. The complexity of an attack is rather high. The exploitation appears to be difficult. The exploit has been disclosed to the public and may be used. The associated identifier of this vulnerability is VDB-249151.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2023-7148
- https://drive.google.com/file/d/1ST3dD-iwUBgBNZ8tGaBbqVi1zRh5rLND/view
- https://github.com/ShifuML/shifu
- https://github.com/ShifuML/shifu/blob/20f589158adfc011c505664cf7bdf31e36ed62fa/src/main/java/ml/shifu/shifu/core/DataPurifier.java
- https://vuldb.com/?ctiid.249151
- https://vuldb.com/?id.249151
