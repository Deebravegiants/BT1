# [M] Ember.js Potential XSS Exploit When Binding `tagName` to User-Supplied Data

## Summary
Severity: Medium
Advisory: GHSA-5m48-c37x-f792
CVE: CVE-2013-4170
CWE: CWE-79
Ecosystem: RubyGems
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:R/S:C/C:L/I:L/A:N (CVSS_V3)
Published: 2022-07-01
Source: https://github.com/advisories/GHSA-5m48-c37x-f792
Type: github-advisory

## Affected
- RubyGems: `ember-source` — affected >=0 <1.0.0.rc1.1
- RubyGems: `ember-source` — affected >=1.0.0.rc2.0 <1.0.0.rc2.1
- RubyGems: `ember-source` — affected >=1.0.0.rc3.0 <1.0.0.rc3.1
- RubyGems: `ember-source` — affected >=1.0.0.rc4.0 <1.0.0.rc4.1
- RubyGems: `ember-source` — affected >=1.0.0.rc5.0 <1.0.0.rc5.1
- RubyGems: `ember-source` — affected >=1.0.0.rc6.0 <1.0.0.rc6.1

## Details
In general, Ember.js escapes or strips any user-supplied content before inserting it in strings that will be sent to innerHTML. However, the `tagName` property of an `Ember.View` was inserted into such a string without being sanitized. This means that if an application assigns a view's `tagName` to user-supplied data, a specially-crafted payload could execute arbitrary JavaScript in the context of the current domain ("XSS"). This vulnerability only affects applications that assign or bind user-provided content to `tagName`.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2013-4170
- https://github.com/emberjs/ember.js
- https://github.com/rubysec/ruby-advisory-db/blob/master/gems/ember-source/CVE-2013-4170.yml
- https://groups.google.com/forum/#!topic/ember-security/dokLVwwxAdM
- https://groups.google.com/g/ember-security/c/dokLVwwxAdM
- https://rubysec.com/advisories/CVE-2013-4170
- https://security.snyk.io/vuln/SNYK-RUBY-EMBERSOURCE-20102
