# [H] Arbitrary Code Execution in Rdoc

## Summary
Severity: High
Advisory: GHSA-ggxm-pgc9-g7fp
CVE: CVE-2021-31799
CWE: CWE-74, CWE-77, CWE-78
Ecosystem: RubyGems
CVSS: CVSS:3.1/AV:L/AC:H/PR:L/UI:N/S:U/C:H/I:H/A:H (CVSS_V3)
Published: 2021-09-01
Source: https://github.com/advisories/GHSA-ggxm-pgc9-g7fp
Type: github-advisory

## Affected
- RubyGems: `rdoc` — affected >=3.11 <6.1.2.1
- RubyGems: `rdoc` — affected >=6.2.0 <6.2.1.1
- RubyGems: `rdoc` — affected >=6.3.0 <6.3.1

## Details
In RDoc 3.11 through 6.x before 6.3.1, as distributed with Ruby through 3.0.1, it is possible to execute arbitrary code via | and tags in a filename.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2021-31799
- https://github.com/ruby/rdoc/commit/a7f5d6ab88632b3b482fe10611382ff73d14eed7
- https://github.com/ruby/rdoc
- https://github.com/rubysec/ruby-advisory-db/blob/master/gems/rdoc/CVE-2021-31799.yml
- https://lists.debian.org/debian-lts-announce/2021/10/msg00009.html
- https://security-tracker.debian.org/tracker/CVE-2021-31799
- https://security.gentoo.org/glsa/202401-05
- https://security.netapp.com/advisory/ntap-20210902-0004
- https://www.oracle.com/security-alerts/cpuapr2022.html
- https://www.ruby-lang.org/en/news/2021/05/02/os-command-injection-in-rdoc
