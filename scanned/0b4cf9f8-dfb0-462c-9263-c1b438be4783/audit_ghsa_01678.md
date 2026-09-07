# [M] Cross-Site Scripting in Kaminari

## Summary
Severity: Medium
Advisory: GHSA-r5jw-62xg-j433
CVE: CVE-2020-11082
CWE: CWE-79
Ecosystem: RubyGems
CVSS: CVSS:3.1/AV:N/AC:H/PR:N/UI:R/S:U/C:H/I:L/A:L (CVSS_V3)
Published: 2020-05-28
Source: https://github.com/advisories/GHSA-r5jw-62xg-j433
Type: github-advisory

## Affected
- RubyGems: `kaminari` — affected >=0 <1.2.1

## Details
### Impact
In Kaminari before 1.2.1, there is a vulnerability that would allow an attacker to inject arbitrary code into pages with pagination links. This has been fixed in 1.2.1.

### Releases
The 1.2.1 gem including the patch has already been released.
All past released versions are affected by this vulnerability.

### Workarounds
Application developers who can't update the gem can workaround by overriding the `PARAM_KEY_EXCEPT_LIST` constant.

```ruby
module Kaminari::Helpers
  PARAM_KEY_EXCEPT_LIST = [:authenticity_token, :commit, :utf8, :_method, :script_name, :original_script_name].freeze
end
```

### Credits
Thanks to Daniel Mircea for finding the issue and sending a patch via GitHub. Also thanks to Aditya Prakash for reporting the vulnerability.

## References
- https://github.com/kaminari/kaminari/security/advisories/GHSA-r5jw-62xg-j433
- https://nvd.nist.gov/vuln/detail/CVE-2020-11082
- https://github.com/github/advisory-review/pull/1020
- https://github.com/kaminari/kaminari/commit/8dd52a1aed3d2fa2835d836de23fc0d8c4ff5db8
- https://github.com/kaminari/kaminari
- https://github.com/rubysec/ruby-advisory-db/blob/master/gems/kaminari/CVE-2020-11082.yml
- https://lists.debian.org/debian-lts-announce/2021/09/msg00011.html
- https://www.debian.org/security/2021/dsa-5005
