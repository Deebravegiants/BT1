# [M] ember-source Cross-site Scripting vulnerability

## Summary
Severity: Medium
Advisory: GHSA-m3q7-rj8g-m457
CVE: CVE-2015-7565
CWE: CWE-79
Ecosystem: RubyGems
CVSS: CVSS:3.0/AV:N/AC:L/PR:N/UI:R/S:C/C:L/I:L/A:N (CVSS_V3)
Published: 2018-08-28
Source: https://github.com/advisories/GHSA-m3q7-rj8g-m457
Type: github-advisory

## Affected
- RubyGems: `ember-source` — affected >=1.8.0 <1.11.4
- RubyGems: `ember-source` — affected >=1.12.0 <1.12.2
- RubyGems: `ember-source` — affected >=1.13.0 <1.13.12
- RubyGems: `ember-source` — affected >=2.0.0 <2.0.3
- RubyGems: `ember-source` — affected >=2.1.0 <2.1.2
- RubyGems: `ember-source` — affected >=2.2.0 <2.2.1

## Details
Cross-site scripting (XSS) vulnerability in Ember.js 1.8.x through 1.10.x, 1.11.x before 1.11.4, 1.12.x before 1.12.2, 1.13.x before 1.13.12, 2.0.x before 2.0.3, 2.1.x before 2.1.2, and 2.2.x before 2.2.1 allows remote attackers to inject arbitrary web script or HTML.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2015-7565
- https://github.com/rubysec/ruby-advisory-db/blob/master/gems/ember-source/CVE-2015-7565.yml
- https://groups.google.com/forum/#!topic/ember-security/OfyQkoSuppY
- http://emberjs.com/blog/2016/01/14/security-releases-ember-1-11-4-1-12-2-1-13-12-2-0-3-2-1-2-2-2-1.html
