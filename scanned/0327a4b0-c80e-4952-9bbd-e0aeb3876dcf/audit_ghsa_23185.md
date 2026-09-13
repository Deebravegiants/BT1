# [H] b3log Wide unauthenticated file access

## Summary
Severity: High
Advisory: GHSA-6452-jr93-r5qm
CVE: CVE-2019-13915
CWE: CWE-59, CWE-74
Ecosystem: Go
CVSS: CVSS:3.0/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:N/A:N (CVSS_V3)
Published: 2022-05-24
Source: https://github.com/advisories/GHSA-6452-jr93-r5qm
Type: github-advisory

## Affected
- Go: `github.com/b3log/wide` — affected >=0 <1.6.0

## Details
b3log Wide before 1.6.0 allows three types of attacks to access arbitrary files. First, the attacker can write code in the editor, and compile and run it approximately three times to read an arbitrary file. Second, the attacker can create a symlink, and then place the symlink into a ZIP archive. An unzip operation leads to read access, and write access (depending on file permissions), to the symlink target. Third, the attacker can import a Git repository that contains a symlink, similarly leading to read and write access.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2019-13915
- https://github.com/b3log/wide/issues/355
- https://github.com/b3log/wide
- https://sca.analysiscenter.veracode.com/vulnerability-database/security/arbitrary-file-reads-and-writes/go/sid-20862
- https://web.archive.org/web/20190522035724/https://github.com/b3log/wide
