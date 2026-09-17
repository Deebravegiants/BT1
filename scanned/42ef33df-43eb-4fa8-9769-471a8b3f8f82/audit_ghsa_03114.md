# [H] Tempfile on Windows path traversal vulnerability

## Summary
Severity: High
Advisory: GHSA-46f2-3v63-3xrp
CVE: CVE-2021-28966
CWE: CWE-22
Ecosystem: RubyGems
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:H/A:N (CVSS_V3)
Published: 2021-05-06
Source: https://github.com/advisories/GHSA-46f2-3v63-3xrp
Type: github-advisory

## Affected
- RubyGems: `tmpdir` — affected >=0 <0.1.2

## Details
There is an unintentional directory creation vulnerability in `tmpdir` library bundled with Ruby on Windows. And there is also an unintentional file creation vulnerability in tempfile library bundled with Ruby on Windows, because it uses tmpdir internally.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2021-28966
- https://github.com/ruby/tmpdir/pull/8
- https://github.com/ruby/tmpdir/commit/93798c01cb7c10476e50a4d80130a329ba47f348
- https://hackerone.com/reports/1131465
- https://github.com/ruby/tmpdir
- https://github.com/rubysec/ruby-advisory-db/blob/master/gems/tmpdir/CVE-2021-28966.yml
- https://rubygems.org/gems/tmpdir
- https://security.netapp.com/advisory/ntap-20210902-0004
- https://www.ruby-lang.org/en/news/2021/04/05/tempfile-path-traversal-on-windows-cve-2021-28966
