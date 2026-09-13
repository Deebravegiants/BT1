# [H] fastreader Gem for Ruby URI Handling Arbitrary Command Injection

## Summary
Severity: High
Advisory: GHSA-w248-xr37-jx8m
CVE: CVE-2013-2615
CWE: CWE-94
Ecosystem: RubyGems
Published: 2017-10-24
Source: https://github.com/advisories/GHSA-w248-xr37-jx8m
Type: github-advisory

## Affected
- RubyGems: `fastreader` — affected >=1.0.0

## Details
fastreader Gem for Ruby contains a flaw that is triggered during the handling of specially crafted input passed via a URL that contains a ';' character. This may allow a context-dependent attacker to potentially execute arbitrary commands.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2013-2615
- https://github.com/rubysec/ruby-advisory-db/blob/master/gems/fastreader/CVE-2013-2615.yml
- http://packetstormsecurity.com/files/120776/Ruby-Gem-Fastreader-1.0.8-Command-Execution.html
- http://packetstormsecurity.com/files/120845/Ruby-Gem-Fastreader-1.0.8-Code-Execution.html
- http://seclists.org/fulldisclosure/2013/Mar/122
- http://www.openwall.com/lists/oss-security/2013/03/19/9
