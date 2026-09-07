# [M] Gon gem lack of escaping certain input when outputting as JSON

## Summary
Severity: Medium
Advisory: GHSA-78vq-9j56-wrfr
CVE: CVE-2020-25739
CWE: CWE-79
Ecosystem: RubyGems
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:R/S:C/C:L/I:L/A:N (CVSS_V3)
Published: 2021-04-30
Source: https://github.com/advisories/GHSA-78vq-9j56-wrfr
Type: github-advisory

## Affected
- RubyGems: `gon` — affected >=0 <6.4.0

## Details
An issue was discovered in the gon gem before gon-6.4.0 for Ruby. MultiJson does not honor the escape_mode parameter to escape fields as an XSS protection mechanism. To mitigate, json_dumper.rb in gon now does escaping for XSS by default without relying on MultiJson.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2020-25739
- https://github.com/gazay/gon/commit/fe3c7b2191a992386dc9edd37de5447a4e809bc7
- https://github.com/gazay/gon
- https://github.com/rubysec/ruby-advisory-db/blob/master/gems/gon/CVE-2020-25739.yml
- https://lists.debian.org/debian-lts-announce/2020/09/msg00018.html
- https://usn.ubuntu.com/4560-1
