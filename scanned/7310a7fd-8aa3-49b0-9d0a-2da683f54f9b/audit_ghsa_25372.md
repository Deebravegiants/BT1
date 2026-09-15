# [H] fs-git command injection vulnerability

## Summary
Severity: High
Advisory: GHSA-wp3j-gv53-4pg8
CVE: CVE-2017-1000451
CWE: CWE-78
Ecosystem: npm
CVSS: CVSS:3.0/AV:L/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H (CVSS_V3)
Published: 2022-05-13
Source: https://github.com/advisories/GHSA-wp3j-gv53-4pg8
Type: github-advisory

## Affected
- npm: `fs-git` — affected >=0 <1.0.2

## Details
fs-git is a file system like api for git repository. The fs-git version 1.0.1 module relies on child_process.exec, however, the buildCommand method used to construct exec strings does not properly sanitize data and is vulnerable to command injection across all methods that use it and call exec.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2017-1000451
- https://github.com/vvakame/fs-git/commit/eb5f70efa5cfbff1ab299fa7daaa5de549243998
- https://nodesecurity.io/advisories/360
