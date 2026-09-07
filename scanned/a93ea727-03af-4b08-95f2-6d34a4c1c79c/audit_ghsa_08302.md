# [M] CSS Parser: Improper Certificate Validation allows MITM injection of remote CSS content

## Summary
Severity: Medium
Advisory: GHSA-ff6c-w6qf-7xqc
CVE: CVE-2026-44312
CWE: CWE-295, CWE-829
Ecosystem: RubyGems
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:C/C:N/I:L/A:N (CVSS_V3)
Published: 2026-05-07
Source: https://github.com/advisories/GHSA-ff6c-w6qf-7xqc
Type: github-advisory

## Affected
- RubyGems: `css_parser` — affected >=2.0.0 <2.1.0
- RubyGems: `css_parser` — affected >=0 <1.22.0

## Details
### Summary

The CSS Parser gem does not validate HTTPS connections, allowing a Man-in-the-Middle (MITM) attacker to inject or modify CSS content when stylesheets are loaded via HTTPS. The connection is established with `OpenSSL::SSL::VERIFY_NONE`, meaning any HTTPS certificate—even entirely untrusted—will be accepted without validation.

### Details

In `lib/css_parser/parser.rb`, the HTTP client sets:
https://github.com/premailer/css_parser/blob/3f91e8db7547fac50ab50cb7f9920f785f722740/lib/css_parser/parser.rb#L646

```ruby
http.verify_mode = OpenSSL::SSL::VERIFY_NONE
```

As a result, the library does not validate the authenticity of HTTPS connections and does not protect against man-in-the-middle attacks. Any attacker in a position to intercept network traffic can inject or modify CSS loaded via HTTPS URLs without detection or warning.

### PoC

1. Set up a test Ruby project that uses the CSS Parser gem and loads an external stylesheet over HTTPS.
2. Use a local proxy (such as mitmproxy or Burp Suite) to intercept outgoing HTTPS requests.
3. Present a fake self-signed certificate to the client.
4. Inject custom CSS into the intercepted HTTPS response.
   
The request will succeed and the injected CSS will be delivered to the application, as the connection is not validated.

### References
 
https://github.com/premailer/css_parser/issues/185

### Impact

Applications using CSS Parser to load remote stylesheets over HTTPS are vulnerable to CSS injection and content manipulation, regardless of the trust status of the remote server. All users who use CSS Parser to fetch external CSS over HTTPS may be impacted.

### Credit

This vulnerability was uncovered by @JLLeitschuh of the @braze-inc security team.

## References
- https://github.com/premailer/css_parser/security/advisories/GHSA-ff6c-w6qf-7xqc
- https://nvd.nist.gov/vuln/detail/CVE-2026-44312
- https://github.com/premailer/css_parser/issues/185
- https://github.com/premailer/css_parser/commit/35e689c904225add78e0c488cf04bad052666449
- https://github.com/premailer/css_parser/commit/e0c95d5abe91b237becb90ff316531a6547ada18
- https://github.com/premailer/css_parser
- https://github.com/rubysec/ruby-advisory-db/blob/master/gems/css_parser/CVE-2026-44312.yml
