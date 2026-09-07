# [H] Remote code execution via user-provided local names in ActionView

## Summary
Severity: High
Advisory: GHSA-cr3x-7m39-c6jq
CVE: CVE-2020-8163
CWE: CWE-94
Ecosystem: RubyGems
CVSS: CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H (CVSS_V3)
Published: 2020-07-07
Source: https://github.com/advisories/GHSA-cr3x-7m39-c6jq
Type: github-advisory

## Affected
- RubyGems: `actionview` — affected >=0 <4.2.11.3

## Details
The is a code injection vulnerability in versions of Rails prior to 5.0.1 that would allow an attacker who controlled the `locals` argument of a `render` call to perform a RCE.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2020-8163
- https://hackerone.com/reports/304805
- https://github.com/rubysec/ruby-advisory-db/blob/master/gems/actionview/CVE-2020-8163.yml
- https://groups.google.com/forum/#!topic/rubyonrails-security/hWuKcHyoKh0
- https://groups.google.com/g/rubyonrails-security/c/hWuKcHyoKh0
- https://lists.debian.org/debian-lts-announce/2020/07/msg00013.html
- http://packetstormsecurity.com/files/158604/Ruby-On-Rails-5.0.1-Remote-Code-Execution.html
