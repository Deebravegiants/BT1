# [H] Cross-site Scripting (XSS) possible due to improper sanitisation of `href` attributes on `<a>` tags

## Summary
Severity: High
Advisory: GHSA-g7xq-xv8c-h98c
CVE: CVE-2024-32463
CWE: CWE-79, CWE-87
Ecosystem: RubyGems
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:R/S:U/C:H/I:L/A:N (CVSS_V3)
Published: 2024-04-17
Source: https://github.com/advisories/GHSA-g7xq-xv8c-h98c
Type: github-advisory

## Affected
- RubyGems: `phlex` — affected >=1.10.0 <1.10.1
- RubyGems: `phlex` — affected >=1.9.0 <1.9.2
- RubyGems: `phlex` — affected >=1.8.0 <1.8.3
- RubyGems: `phlex` — affected >=1.7.0 <1.7.2
- RubyGems: `phlex` — affected >=1.6.0 <1.6.3
- RubyGems: `phlex` — affected >=1.5.0 <1.5.3
- RubyGems: `phlex` — affected >=0 <1.4.2

## Details
### Summary
There is a potential cross-site scripting (XSS) vulnerability that can be exploited via maliciously crafted user data.

Our filter to detect and prevent the use of the `javascript:` URL scheme in the `href` attribute of an `<a>` tag could be bypassed with tab `\t` or newline `\n` characters between the characters of the protocol, e.g. `java\tscript:`.

### Impact

If you render an `<a>` tag with an `href` attribute set to a user-provided link, that link could potentially execute JavaScript when clicked by another user.

```ruby
a(href: user_profile) { "Profile" }
```

### Mitigation

The best way to mitigate this vulnerability is to update to one of the following versions:

- [1.10.1](https://rubygems.org/gems/phlex/versions/1.10.1)
- [1.9.2](https://rubygems.org/gems/phlex/versions/1.9.2)
- [1.8.3](https://rubygems.org/gems/phlex/versions/1.8.3)
- [1.7.2](https://rubygems.org/gems/phlex/versions/1.7.2)
- [1.6.3](https://rubygems.org/gems/phlex/versions/1.6.3)
- [1.5.3](https://rubygems.org/gems/phlex/versions/1.5.3)
- [1.4.2](https://rubygems.org/gems/phlex/versions/1.4.2)

### Workarounds
Configuring a [Content Security Policy](https://developer.mozilla.org/en-US/docs/Web/HTTP/Headers/Content-Security-Policy) that does not allow [`unsafe-inline`](https://developer.mozilla.org/en-US/docs/Web/HTTP/Headers/Content-Security-Policy#unsafe-inline) would effectively prevent this vulnerability from being exploited.

## References
- https://github.com/phlex-ruby/phlex/security/advisories/GHSA-g7xq-xv8c-h98c
- https://nvd.nist.gov/vuln/detail/CVE-2024-32463
- https://github.com/phlex-ruby/phlex/commit/9e3f5b980655817993682e409cbda72956d865cb
- https://developer.mozilla.org/en-US/docs/Web/HTTP/Headers/Content-Security-Policy
- https://developer.mozilla.org/en-US/docs/Web/HTTP/Headers/Content-Security-Policy#unsafe-inline
- https://github.com/phlex-ruby/phlex
- https://github.com/rubysec/ruby-advisory-db/blob/master/gems/phlex/CVE-2024-32463.yml
