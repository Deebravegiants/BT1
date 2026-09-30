# [M] CVE-2018-1002206

## Summary
Severity: Medium
Advisory: CVE-2018-1002206
Aliases: GHSA-fxh6-w476-hgr4
CVSS: 5.5 (CVSS:3.0/AV:L/AC:L/PR:N/UI:R/S:U/C:N/I:H/A:N)
Published: 2018-07-25
Source: https://osv.dev/vulnerability/CVE-2018-1002206
Type: osv

## Details
SharpCompress before 0.21.0 is vulnerable to directory traversal, allowing attackers to write to arbitrary files via a ../ (dot dot slash) in a Zip archive entry that is mishandled during extraction. This vulnerability is also known as 'Zip-Slip'.

## References
- https://github.com/adamhathcock/sharpcompress/commit/42b1205fb435de523e6ef8ac5b7bafbe712997f6
- https://github.com/adamhathcock/sharpcompress/pull/374
- https://github.com/snyk/zip-slip-vulnerability
- https://snyk.io/research/zip-slip-vulnerability
- https://snyk.io/vuln/SNYK-DOTNET-SHARPCOMPRESS-60246
