# [H] hutool-core discovered to contain an infinite loop in the StrSplitter.splitByRegex function

## Summary
Severity: High
Advisory: GHSA-7m7h-rgvp-3v4r
CVE: CVE-2023-51075
CWE: CWE-835
Ecosystem: Maven
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:H (CVSS_V3)
Published: 2023-12-27
Source: https://github.com/advisories/GHSA-7m7h-rgvp-3v4r
Type: github-advisory

## Affected
- Maven: `cn.hutool:hutool-core` — affected >=0 <5.8.24

## Details
hutool-core v5.8.23 was discovered to contain an infinite loop in the StrSplitter.splitByRegex function. This vulnerability allows attackers to cause a Denial of Service (DoS) via manipulation of the first two parameters.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2023-51075
- https://github.com/dromara/hutool/issues/3421
- https://github.com/dromara/hutool/commit/32f2d0bd55defecb869fbf64d940bcc05642accc
- https://github.com/dromara/hutool
