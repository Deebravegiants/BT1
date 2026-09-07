# [M] layui vulnerable to cross-site scripting

## Summary
Severity: Medium
Advisory: GHSA-hx4h-676r-j3qp
CVE: CVE-2023-3691
CWE: CWE-79
Ecosystem: npm
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:R/S:C/C:L/I:L/A:N (CVSS_V3)
Published: 2023-07-16
Source: https://github.com/advisories/GHSA-hx4h-676r-j3qp
Type: github-advisory

## Affected
- npm: `layui` — affected >=0 <2.8.0

## Details
A vulnerability, which was classified as problematic, was found in layui up to v2.8.0-rc.16. This affects an unknown part of the component HTML Attribute Handler. The manipulation of the argument title leads to cross site scripting. It is possible to initiate the attack remotely. Upgrading to version 2.8.0 is able to address this issue. It is recommended to upgrade the affected component. The identifier VDB-234237 was assigned to this vulnerability.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2023-3691
- https://gitee.com/layui/layui/issues/I7HDXZ
- https://gitee.com/layui/layui/tree/v2.8.0
- https://github.com/layui/layui
- https://vuldb.com/?ctiid.234237
- https://vuldb.com/?id.234237
