# [C] Creme Fraiche contains OS Command Injection

## Summary
Severity: Critical
Advisory: GHSA-m6f7-46hw-grcj
CVE: CVE-2013-2090
CWE: CWE-78
Ecosystem: RubyGems
Published: 2017-10-24
Source: https://github.com/advisories/GHSA-m6f7-46hw-grcj
Type: github-advisory

## Affected
- RubyGems: `cremefraiche` — affected >=0 <0.6.1

## Details
The set_meta_data function in lib/cremefraiche.rb in the Creme Fraiche gem before 0.6.1 for Ruby allows remote attackers to execute arbitrary commands via shell metacharacters in the file name of an email attachment.  NOTE: some of these details are obtained from third party information.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2013-2090
- http://packetstormsecurity.com/files/121635/Ruby-Gem-Creme-Fraiche-0.6-Command-Injection.html
- http://www.vapid.dhs.org/advisories/cremefraiche-cmd-inj.html
