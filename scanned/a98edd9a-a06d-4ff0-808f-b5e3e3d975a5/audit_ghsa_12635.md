# [H] Insecure Temporary File in HuTool

## Summary
Severity: High
Advisory: GHSA-7mcw-xmx3-7p8m
CVE: CVE-2023-33695
CWE: CWE-377, CWE-732
Ecosystem: Maven
CVSS: CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:N (CVSS_V3)
Published: 2023-06-13
Source: https://github.com/advisories/GHSA-7mcw-xmx3-7p8m
Type: github-advisory

## Affected
- Maven: `cn.hutool:hutool-core` — affected >=0 <5.8.19

## Details
Hutool v5.8.17 and below was discovered to contain an information disclosure vulnerability via the `File.createTempFile()` function at `/core/io/FileUtil.java`.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2023-33695
- https://github.com/dromara/hutool/issues/3103
- https://github.com/dromara/hutool/commit/c33550f703f5d1d7dd71ad2992d79a5e5532ce2c
- https://github.com/dromara/hutool
