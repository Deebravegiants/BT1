# [H] Phlex vulnerable to Cross-site Scripting (XSS) via maliciously formed HTML attribute names and values

## Summary
Severity: High
Advisory: GHSA-9p57-h987-4vgx
CVE: CVE-2024-32970
CWE: CWE-79
Ecosystem: RubyGems
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:R/S:U/C:H/I:L/A:N (CVSS_V3)
Published: 2024-05-01
Source: https://github.com/advisories/GHSA-9p57-h987-4vgx
Type: github-advisory

## Affected
- RubyGems: `phlex` — affected >=0 <1.9.3
- RubyGems: `phlex` — affected >=1.10.0 <1.10.2

## Details
There is a potential cross-site scripting (XSS) vulnerability that can be exploited via maliciously crafted user data.

The reason these issues were not detected before is the escapes were working as designed. However, their design didn't take into account just how recklessly permissive browser are when it comes to executing unsafe JavaScript via HTML attributes.

### Impact

If you render an `<a>` tag with an `href` attribute set to a user-provided link, that link could potentially execute JavaScript when clicked by another user.

```ruby
a(href: user_profile) { "Profile" }
```

If you splat user-provided attributes when rendering any HTML or SVG tag, malicious event attributes could be included in the output, executing JavaScript when the events are triggered by another user.

```ruby
h1(**JSON.parse(user_attributes))
```

### Patches
Patches are [available on RubyGems](https://rubygems.org/gems/phlex) for all minor versions released in the last year.

- [1.10.2](https://rubygems.org/gems/phlex/versions/1.10.2)
- [1.9.3](https://rubygems.org/gems/phlex/versions/1.9.3)

If you are on `main`, it has been patched since [`da8f943`](https://github.com/phlex-ruby/phlex/commit/da8f94342a84cff9d78c98bcc3b3604ee2e577d2)

### Workarounds
Configuring a [Content Security Policy](https://developer.mozilla.org/en-US/docs/Web/HTTP/Headers/Content-Security-Policy) that does not allow [`unsafe-inline`](https://developer.mozilla.org/en-US/docs/Web/HTTP/Headers/Content-Security-Policy#unsafe-inline) would effectively prevent this vulnerability from being exploited.

### References

In addition to upgrading to a patched version of Phlex, we strongly recommend configuring a Content Security Policy header that does not allow `unsafe-inline`. Here’s how you can configure a Content Security Policy header in Rails. https://guides.rubyonrails.org/security.html#content-security-policy-header

## References
- https://github.com/phlex-ruby/phlex/security/advisories/GHSA-9p57-h987-4vgx
- https://nvd.nist.gov/vuln/detail/CVE-2024-32970
- https://github.com/phlex-ruby/phlex/commit/da8f94342a84cff9d78c98bcc3b3604ee2e577d2
- https://developer.mozilla.org/en-US/docs/Web/HTTP/Headers/Content-Security-Policy
- https://developer.mozilla.org/en-US/docs/Web/HTTP/Headers/Content-Security-Policy#unsafe-inline
- https://github.com/payloadbox/xss-payload-list
- https://github.com/phlex-ruby/phlex
- https://github.com/rubysec/ruby-advisory-db/blob/master/gems/phlex/CVE-2024-32970.yml
- https://rubygems.org/gems/phlex
- https://rubygems.org/gems/phlex/versions/1.10.2
- https://rubygems.org/gems/phlex/versions/1.9.3
