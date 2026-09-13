# [M] Rack vulnerable to ReDoS in content type parsing (2nd degree polynomial)

## Summary
Severity: Medium
Advisory: GHSA-22f2-v57c-j9cx
CVE: CVE-2024-25126
CWE: CWE-1333
Ecosystem: RubyGems
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:L (CVSS_V3)
Published: 2024-02-28
Source: https://github.com/advisories/GHSA-22f2-v57c-j9cx
Type: github-advisory

## Affected
- RubyGems: `rack` — affected >=3.0.0 <3.0.9.1
- RubyGems: `rack` — affected >=0.4 <2.2.8.1

## Details
### Summary

```ruby
module Rack
  class MediaType
    SPLIT_PATTERN = %r{\s*[;,]\s*}
```
The above regexp is subject to ReDos. 50K blank characters as a prefix to the header will take over 10s to split.

### PoC

A simple HTTP request with lots of blank characters in the content-type header:

```ruby
request["Content-Type"] = (" " * 50_000) + "a,"
```

### Impact

It's a very easy to craft ReDoS. Like all ReDoS the impact is debatable.

## References
- https://github.com/rack/rack/security/advisories/GHSA-22f2-v57c-j9cx
- https://nvd.nist.gov/vuln/detail/CVE-2024-25126
- https://github.com/rack/rack/commit/6efb2ceea003c4b195815a614e00438cbd543462
- https://github.com/rack/rack/commit/d9c163a443b8cadf4711d84bd2c58cb9ef89cf49
- https://discuss.rubyonrails.org/t/denial-of-service-vulnerability-in-rack-content-type-parsing/84941
- https://github.com/rack/rack
- https://github.com/rubysec/ruby-advisory-db/blob/master/gems/rack/CVE-2024-25126.yml
- https://lists.debian.org/debian-lts-announce/2024/04/msg00022.html
- https://security.netapp.com/advisory/ntap-20240510-0005
