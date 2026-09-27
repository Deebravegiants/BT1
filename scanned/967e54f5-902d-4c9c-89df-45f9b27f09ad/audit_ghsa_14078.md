# [C] Server-side template injection in beetl

## Summary
Severity: Critical
Advisory: GHSA-m69h-4frq-vwq7
CVE: CVE-2023-30331
Ecosystem: Maven
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H (CVSS_V3)
Published: 2023-05-04
Source: https://github.com/advisories/GHSA-m69h-4frq-vwq7
Type: github-advisory

## Affected
- Maven: `com.ibeetl:beetl` — affected >=0

## Details
An issue in the render function of beetl v3.15.0 allows attackers to execute server-side template injection (SSTI) via a crafted payload.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2023-30331
- https://gitee.com/xiandafu/beetl/issues/I6RUIP
- https://github.com/javamonkey/beetl2.0
- https://github.com/luelueking/Beetl-3.15.0-vuln-poc
