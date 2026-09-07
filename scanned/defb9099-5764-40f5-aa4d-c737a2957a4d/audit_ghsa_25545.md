# [M] Cross-site Scripting Vulnerability in Action Pack

## Summary
Severity: Medium
Advisory: GHSA-mm33-5vfq-3mm3
CVE: CVE-2022-22577
CWE: CWE-79
Ecosystem: RubyGems
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:R/S:C/C:L/I:L/A:N (CVSS_V3)
Published: 2022-04-27
Source: https://github.com/advisories/GHSA-mm33-5vfq-3mm3
Type: github-advisory

## Affected
- RubyGems: `actionpack` — affected >=5.2.0 <5.2.7.1
- RubyGems: `actionpack` — affected >=6.0.0 <6.0.4.8
- RubyGems: `actionpack` — affected >=6.1.0 <6.1.5.1
- RubyGems: `actionpack` — affected >=7.0.0 <7.0.2.4

## Details
There is a possible XSS vulnerability in Rails / Action Pack. This vulnerability has been
assigned the CVE identifier CVE-2022-22577.

Versions Affected:  >= 5.2.0
Not affected:       < 5.2.0
Fixed Versions:     7.0.2.4, 6.1.5.1, 6.0.4.8, 5.2.7.1

## Impact

CSP headers were only sent along with responses that Rails considered as
"HTML" responses.  This left API requests without CSP headers, which could
possibly expose users to XSS attacks.

## Releases

The FIXED releases are available at the normal locations.

## Workarounds

Set a CSP for your API responses manually.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2022-22577
- https://github.com/rails/rails/pull/44635
- https://github.com/rails/rails/commit/2b820a2a69fa50cffa74b4aedc57bf92ed6910ec
- https://github.com/rails/rails/commit/5299b57d596ea274f77f5ffee2b79c6ee0255508
- https://github.com/rails/rails/commit/8198d7c4accad0b6ba956b9d59528534a289866b
- https://github.com/rails/rails/commit/d2253115ac2b30f5f7210670af906cebf79cf809
- https://discuss.rubyonrails.org/t/cve-2022-22577-possible-xss-vulnerability-in-action-pack/80533
- https://github.com/rails/rails
- https://github.com/rubysec/ruby-advisory-db/blob/master/gems/actionpack/CVE-2022-22577.yml
- https://groups.google.com/g/ruby-security-ann/c/NuFRKaN5swI
- https://lists.debian.org/debian-lts-announce/2022/09/msg00002.html
- https://rubyonrails.org/2022/4/26/Rails-7-0-2-4-6-1-5-1-6-0-4-8-and-5-2-7-1-have-been-released
- https://security.netapp.com/advisory/ntap-20221118-0002
- https://www.debian.org/security/2023/dsa-5372
