# [M] Mingsoft MCMS Cross-site Scripting vulnerability

## Summary
Severity: Medium
Advisory: GHSA-6rvv-h8g7-728w
CVE: CVE-2022-4640
CWE: CWE-79
Ecosystem: Maven
CVSS: CVSS:3.1/AV:N/AC:L/PR:L/UI:R/S:C/C:L/I:L/A:N (CVSS_V3)
Published: 2022-12-22
Source: https://github.com/advisories/GHSA-6rvv-h8g7-728w
Type: github-advisory

## Affected
- Maven: `net.mingsoft:ms-mcms` — affected >=0

## Details
A vulnerability has been found in Mingsoft MCMS 5.2.9 and classified as problematic. Affected by this vulnerability is the function save of the component Article Handler. The manipulation leads to cross site scripting. The attack can be launched remotely. The exploit has been disclosed to the public and may be used. It is recommended to upgrade the affected component. The associated identifier of this vulnerability is VDB-216499.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2022-4640
- https://gitee.com/mingSoft/MCMS/issues/I65KI5
- https://vuldb.com/?id.216499
