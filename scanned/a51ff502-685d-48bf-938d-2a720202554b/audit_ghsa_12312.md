# [H] nori contains Improper Input Validation

## Summary
Severity: High
Advisory: GHSA-4936-rj25-6wm6
CVE: CVE-2013-0285
CWE: CWE-20
Ecosystem: RubyGems
Published: 2017-10-24
Source: https://github.com/advisories/GHSA-4936-rj25-6wm6
Type: github-advisory

## Affected
- RubyGems: `nori` — affected >=2.0.0 <2.0.2
- RubyGems: `nori` — affected >=1.1.0 <1.1.4
- RubyGems: `nori` — affected >=1.0.0 <1.0.3

## Details
The nori gem 2.0.x before 2.0.2, 1.1.x before 1.1.4, and 1.0.x before 1.0.3 for Ruby does not properly restrict casts of string values, which allows remote attackers to conduct object-injection attacks and execute arbitrary code, or cause a denial of service (memory and CPU consumption) involving nested XML entity references, by leveraging Action Pack support for (1) YAML type conversion or (2) Symbol type conversion, a similar vulnerability to CVE-2013-0156.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2013-0285
- https://github.com/savonrb/nori/commit/2ca6f8603e406f884a8fcea6bc26f8f6bf168f40
- https://github.com/savonrb/nori/commit/4bcf59abdcec6bcd1153241b122eda61a494e4fb
- https://github.com/savonrb/nori/commit/818f5263b1d597b603d46cbe1702cd2717259e32
- https://github.com/savonrb/nori/commit/c3fdce7a2d2670b44f1cda35da0ae73cc1372084
- https://github.com/savonrb/nori/commit/c5e07f5c32e615f0a4a7ee2782d37f7a33261be4
- https://github.com/savonrb/nori/commit/d9b68667249b98776fb23ba9e9c548dc4b524709
- https://github.com/advisories/GHSA-4936-rj25-6wm6
- https://github.com/rubysec/ruby-advisory-db/blob/master/gems/nori/CVE-2013-0285.yml
- https://github.com/savonrb/nori
- https://web.archive.org/web/20130203232028/https://support.cloud.engineyard.com/entries/22915701-january-14-2013-security-vulnerabilities-httparty-extlib-crack-nori-update-these-gems-immediately
- http://seclists.org/oss-sec/2013/q1/304
