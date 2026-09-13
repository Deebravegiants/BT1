# [C] festivaltts4r allows arbitrary command execution

## Summary
Severity: Critical
Advisory: GHSA-f7f4-5w9j-23p2
CVE: CVE-2016-10194
CWE: CWE-77
Ecosystem: RubyGems
CVSS: CVSS:3.0/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H (CVSS_V3)
Published: 2017-10-24
Source: https://github.com/advisories/GHSA-f7f4-5w9j-23p2
Type: github-advisory

## Affected
- RubyGems: `festivaltts4r` — affected >=0

## Details
The festivaltts4r gem for Ruby allows remote attackers to execute arbitrary commands via shell metacharacters in a string to the (1) `to_speech` or (2) `to_mp3` method in `lib/festivaltts4r/festival4r.rb`.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2016-10194
- https://github.com/spejman/festivaltts4r/issues/1
- https://github.com/spejman/festivaltts4r
- http://www.openwall.com/lists/oss-security/2017/01/31/14
- http://www.openwall.com/lists/oss-security/2017/02/02/5
