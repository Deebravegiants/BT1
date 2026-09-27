# [H] Improper Input Validation in tar-fs

## Summary
Severity: High
Advisory: GHSA-x2mc-8fgj-3wmr
CVE: CVE-2018-20835
CWE: CWE-20
Ecosystem: npm
CVSS: CVSS:3.0/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:H/A:N (CVSS_V3)
Published: 2019-05-01
Source: https://github.com/advisories/GHSA-x2mc-8fgj-3wmr
Type: github-advisory

## Affected
- npm: `tar-fs` — affected >=0 <1.16.2

## Details
A vulnerability was found in tar-fs before 1.16.2. An Arbitrary File Overwrite issue exists when extracting a tarball containing a hardlink to a file that already exists on the system, in conjunction with a later plain file with the same name as the hardlink. This plain file content replaces the existing file content.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2018-20835
- https://github.com/mafintosh/tar-fs/commit/06672828e6fa29ac8551b1b6f36c852a9a3c58a2
- https://hackerone.com/reports/344595
- https://github.com/mafintosh/tar-fs/compare/d590fc7...a35ce2f
