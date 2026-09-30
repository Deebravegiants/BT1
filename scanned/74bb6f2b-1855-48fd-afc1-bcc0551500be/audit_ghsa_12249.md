# [C] Shell Metacharacter Injection in kelredd-pruview

## Summary
Severity: Critical
Advisory: GHSA-78j3-7wpm-qhvp
CVE: CVE-2013-1947
CWE: CWE-78
Ecosystem: RubyGems
Published: 2017-10-24
Source: https://github.com/advisories/GHSA-78j3-7wpm-qhvp
Type: github-advisory

## Affected
- RubyGems: `kelredd-pruview` — affected >=0

## Details
kelredd-pruview gem 0.3.8 for Ruby allows context-dependent attackers to execute arbitrary commands via shell metacharacters in a filename argument to document.rb, video.rb, or video_image.rb.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2013-1947
- https://github.com/advisories/GHSA-78j3-7wpm-qhvp
- https://github.com/rubysec/ruby-advisory-db/blob/master/gems/kelredd-pruview/CVE-2013-1947.yml
- http://vapid.dhs.org/advisories/kelredd-pruview-cmd-inject.html
- http://www.openwall.com/lists/oss-security/2013/04/10/3
- http://www.openwall.com/lists/oss-security/2013/04/12/2
