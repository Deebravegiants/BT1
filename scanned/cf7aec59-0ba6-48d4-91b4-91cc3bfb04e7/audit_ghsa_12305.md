# [H] Improper Input Validation in multi_xml

## Summary
Severity: High
Advisory: GHSA-pchc-949f-53m5
CVE: CVE-2013-0175
CWE: CWE-20
Ecosystem: RubyGems
Published: 2017-10-24
Source: https://github.com/advisories/GHSA-pchc-949f-53m5
Type: github-advisory

## Affected
- RubyGems: `multi_xml` — affected >=0 <0.5.2

## Details
multi_xml gem 0.5.2 for Ruby, as used in Grape before 0.2.6 and possibly other products, does not properly restrict casts of string values, which allows remote attackers to conduct object-injection attacks and execute arbitrary code, or cause a denial of service (memory and CPU consumption) involving nested XML entity references, by leveraging support for (1) YAML type conversion or (2) Symbol type conversion, a similar vulnerability to CVE-2013-0156.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2013-0175
- https://github.com/sferik/multi_xml/pull/34
- https://github.com/sferik/multi_xml/commit/c94b136d06822514fc2e99dc851e6c4eeb4c8bdf
- https://github.com/sferik/multi_xml
- https://groups.google.com/forum/?fromgroups=#!topic/ruby-grape/fthDkMgIOa0
- https://news.ycombinator.com/item?id=5040457
- https://www.openwall.com/lists/oss-security/2013/01/11/9
