# [C] Dromara hutool vulnerable to SQL Injection

## Summary
Severity: Critical
Advisory: GHSA-6c25-cxcc-pmc4
CVE: CVE-2023-24163
CWE: CWE-89
Ecosystem: Maven
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H (CVSS_V3)
Published: 2023-01-31
Source: https://github.com/advisories/GHSA-6c25-cxcc-pmc4
Type: github-advisory

## Affected
- Maven: `cn.hutool:hutool-all` — affected >=0 <5.8.21

## Details
SQL Inection vulnerability in Dromara hutool v5.8.11 allows attacker to execute arbitrary code via the aviator template engine.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2023-24163
- https://github.com/dromara/hutool/issues/3149
- https://github.com/google/osv.dev/issues/2195
- https://gitee.com/dromara/hutool
- https://gitee.com/dromara/hutool/issues/I6AJWJ#note_15801868
- https://gitee.com/dromara/hutool/issues/I6AJWJ#note_20057806_link
- https://github.com/dromara/hutool/releases/tag/5.8.21
