# [H] Incorrect Permission Assignment for Critical Resource in NPM

## Summary
Severity: High
Advisory: GHSA-ph34-pc88-72gc
CVE: CVE-2018-7408
CWE: CWE-732
Ecosystem: npm
CVSS: CVSS:3.0/AV:L/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H (CVSS_V3)
Published: 2022-05-13
Source: https://github.com/advisories/GHSA-ph34-pc88-72gc
Type: github-advisory

## Affected
- npm: `npm` — affected >=0 <5.7.1

## Details
An issue was discovered in an npm 5.7.0 2018-02-21 pre-release (marked as "next: 5.7.0" and therefore automatically installed by an "npm upgrade -g npm" command, and also announced in the vendor's blog without mention of pre-release status). It might allow local users to bypass intended filesystem access restrictions because ownerships of /etc and /usr directories are being changed unexpectedly, related to a "correctMkdir" issue.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2018-7408
- https://github.com/npm/npm/issues/19883
- https://github.com/npm/npm/commit/74e149da6efe6ed89477faa81fef08eee7999ad0
- github.com/npm/cli
- http://blog.npmjs.org/post/171169301000/v571
