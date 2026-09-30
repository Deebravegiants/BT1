# [H] degit has a Command Injection issue

## Summary
Severity: High
Advisory: GHSA-77c7-pq4r-6mcq
CVE: CVE-2026-11572
CWE: CWE-77, CWE-78
Ecosystem: npm
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:R/S:U/C:H/I:H/A:H (CVSS_V3)
Published: 2026-06-09
Source: https://github.com/advisories/GHSA-77c7-pq4r-6mcq
Type: github-advisory

## Affected
- npm: `degit` — affected >=0 <2.8.6
- npm: `degit` — affected >=3.0.0 <3.3.1

## Details
Versions of the package degit before 2.8.6, from 3.0.0 and before 3.3.1 are vulnerable to Command Injection due to improper sanitisation of user input for git shell commands directly invoked with exec() method by _cloneWithGit() and fetchRefs() functions. An attacker can execute arbitrary operating system commands as the process user by supplying a specially crafted git repository name.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2026-11572
- https://github.com/Rich-Harris/degit/commit/4ac99e4a4c3f53ca3b5c997bcd7542742ad0c443
- https://github.com/Rich-Harris/degit/commit/d55bfd7cea79c0b387f69ec8477b6c34abf9f226
- https://gist.github.com/badp3te/cf22a939eedbd3d8ade9123827d61639
- https://github.com/Rich-Harris/degit
- https://security.snyk.io/vuln/SNYK-JS-DEGIT-17116207
