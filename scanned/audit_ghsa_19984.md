# [H] HuTool vulnerable to Uncontrolled Resource Consumption

## Summary
Severity: High
Advisory: GHSA-47vx-fqr5-j2gw
CVE: CVE-2022-4565
CWE: CWE-400, CWE-404
Ecosystem: Maven
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:H (CVSS_V3)
Published: 2022-12-16
Source: https://github.com/advisories/GHSA-47vx-fqr5-j2gw
Type: github-advisory

## Affected
- Maven: `cn.hutool:hutool-core` — affected >=0 <5.8.11

## Details
A vulnerability classified as problematic was found in Dromara HuTool up to 5.8.10. This vulnerability affects unknown code of the file cn.hutool.core.util.ZipUtil.java. The manipulation leads to resource consumption. The attack can be initiated remotely. The exploit has been disclosed to the public and may be used. Upgrading to version 5.8.11 is able to address this issue. It is recommended to upgrade the affected component.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2022-4565
- https://github.com/dromara/hutool/issues/2797
- https://github.com/dromara/hutool
- https://vuldb.com/?id.215974
