# [H] SpringBlade vulnerable to SQL injection

## Summary
Severity: High
Advisory: GHSA-62pr-54gv-vg5g
CVE: CVE-2023-40787
CWE: CWE-89
Ecosystem: Maven
Published: 2023-08-29
Source: https://github.com/advisories/GHSA-62pr-54gv-vg5g
Type: github-advisory

## Affected
- Maven: `org.springblade:blade-core-tool` — affected 3.6.0

## Details
In SpringBlade V3.6.0 when executing SQL query, the parameters submitted by the user are not wrapped in quotation marks, which leads to SQL injection.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2023-40787
- https://gist.github.com/kaliwin/9d6cf58bb6ec06765cdf7b75e13ee460
- https://github.com/chillzhuang/blade-tool
- https://sword.bladex.cn
