# [H] Fileutils Command Injection vulnerability

## Summary
Severity: High
Advisory: GHSA-9x97-x2p9-hvpf
CVE: CVE-2013-2516
CWE: CWE-77
Ecosystem: RubyGems
CVSS: CVSS:3.0/AV:N/AC:L/PR:N/UI:R/S:U/C:H/I:H/A:H (CVSS_V3)
Published: 2022-05-14
Source: https://github.com/advisories/GHSA-9x97-x2p9-hvpf
Type: github-advisory

## Affected
- RubyGems: `fileutils` — affected >=0 <0.7.1

## Details
Ruby Gem Fileutils prior to v0.7.1 contains a Command Injection vulnerability in user supplied url variable that is passed to the shell.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2013-2516
- https://github.com/ruby/fileutils/commit/994c7aa1ba391689f844a069b9aee9e49813686c
- https://bugs.ruby-lang.org/issues/7958
- https://github.com/ruby/fileutils
- https://github.com/rubysec/ruby-advisory-db/blob/master/gems/fileutils/CVE-2013-2516.yml
- http://rubygems.org/gems/fileutils
- http://www.vapidlabs.com/advisory.php?v=36
