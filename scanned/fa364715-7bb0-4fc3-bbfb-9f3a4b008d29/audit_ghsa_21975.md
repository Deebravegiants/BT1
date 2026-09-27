# [M] Arbitrary File Write via Archive Extraction in mholt/archiver

## Summary
Severity: Medium
Advisory: GHSA-5wmg-j84w-4jj4
CVE: CVE-2018-1002207
CWE: CWE-22
Ecosystem: Go
CVSS: CVSS:3.0/AV:L/AC:L/PR:N/UI:R/S:U/C:N/I:H/A:N (CVSS_V3)
Published: 2022-02-15
Source: https://github.com/advisories/GHSA-5wmg-j84w-4jj4
Type: github-advisory

## Affected
- Go: `github.com/mholt/archiver` — affected >=0 <2.1.0

## Details
mholt/archiver golang package before e4ef56d48eb029648b0e895bb0b6a393ef0829c3 is vulnerable to directory traversal, allowing attackers to write to arbitrary files via a ../ (dot dot slash) in an archive entry that is mishandled during extraction. This vulnerability is also known as 'Zip-Slip'.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2018-1002207
- https://github.com/mholt/archiver/pull/65
- https://github.com/mholt/archiver/commit/e4ef56d48eb029648b0e895bb0b6a393ef0829c3
- https://github.com/mholt/archiver
- https://github.com/snyk/zip-slip-vulnerability
- https://snyk.io/research/zip-slip-vulnerability
- https://snyk.io/vuln/SNYK-GOLANG-GITHUBCOMMHOLTARCHIVERCMDARCHIVER-50071
