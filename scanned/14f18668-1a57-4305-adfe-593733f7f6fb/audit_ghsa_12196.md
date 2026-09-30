# [H] safemode gem allows context-dependent attackers to obtain sensitive information via the inspect method

## Summary
Severity: High
Advisory: GHSA-c92m-rrrc-q5wf
CVE: CVE-2016-3693
CWE: CWE-200
Ecosystem: RubyGems
CVSS: CVSS:3.0/AV:N/AC:H/PR:N/UI:N/S:U/C:H/I:H/A:H (CVSS_V3)
Published: 2017-10-24
Source: https://github.com/advisories/GHSA-c92m-rrrc-q5wf
Type: github-advisory

## Affected
- RubyGems: `safemode` — affected >=0 <1.2.4

## Details
The Safemode gem before 1.2.4 for Ruby, when initialized with a delegate object that is a Rails controller, allows context-dependent attackers to obtain sensitive information via the inspect method.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2016-3693
- https://github.com/svenfuchs/safemode/commit/0f764a1720a3a68fd2842e21377c8bfad6d7126f
- https://github.com/theforeman/foreman/commit/82f9b93c54f72c5814df6bab7fad057eab65b2f2
- https://access.redhat.com/errata/RHSA-2018:0336
- https://github.com/svenfuchs/safemode
- http://projects.theforeman.org/issues/14635
- http://rubysec.com/advisories/CVE-2016-3693
- http://theforeman.org/security.html#2016-3693
- http://www.openwall.com/lists/oss-security/2016/04/20/8
