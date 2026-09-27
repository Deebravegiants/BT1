# [M] guard-livereload has a directory traversal vulnerability

## Summary
Severity: Medium
Advisory: GHSA-g65v-27r3-5p6m
CVE: CVE-2016-1000305
CWE: CWE-22
Ecosystem: RubyGems
CVSS: CVSS:4.0/AV:N/AC:L/AT:N/PR:N/UI:N/VC:L/VI:N/VA:N/SC:N/SI:N/SA:N (CVSS_V4)
Published: 2026-07-31
Source: https://github.com/advisories/GHSA-g65v-27r3-5p6m
Type: github-advisory

## Affected
- RubyGems: `guard-livereload` — affected >=0 <2.5.2

## Details
The vulnerability allows remote attackers to read arbitrary files
on the server by exploiting improper path validation in the
livereload server functionality.

This vulnerability is related to the handling of file paths in the
livereload server component, which could allow an attacker to traverse
directories and access files outside the intended web root directory.

The issue was identified and reported through the DWF (Distributed
Weakness Filing) project, which assigns CVE identifiers for
security vulnerabilities.

A directory traversal vulnerability exists in
guard-livereload before version 2.5.2.

## References
- https://github.com/guard/guard-livereload/issues/159
- https://github.com/guard/guard-livereload/pull/158
- https://github.com/guard/guard-livereload/commit/0e98469e6b9d81a5bd415781534a23d087c271f8
- https://github.com/guard/guard-livereload
- https://github.com/rubysec/ruby-advisory-db/blob/master/gems/guard-livereload/CVE-2016-1000305.yml
- https://security.snyk.io/vuln/SNYK-RUBY-GUARDLIVERELOAD-20361
