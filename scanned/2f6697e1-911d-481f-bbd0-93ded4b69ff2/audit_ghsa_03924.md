# [H] Prototype Pollution in lodash

## Summary
Severity: High
Advisory: GHSA-4xc9-xhrj-v574
CVE: CVE-2018-16487
CWE: CWE-400
Ecosystem: RubyGems, npm
Published: 2019-02-07
Source: https://github.com/advisories/GHSA-4xc9-xhrj-v574
Type: github-advisory

## Affected
- npm: `lodash` — affected >=0 <4.17.11
- RubyGems: `lodash-rails` — affected >=0 <4.17.11

## Details
Versions of `lodash` before 4.17.11 are vulnerable to prototype pollution. 

The vulnerable functions are 'defaultsDeep', 'merge', and 'mergeWith' which allow a malicious user to modify the prototype of `Object` via `{constructor: {prototype: {...}}}` causing the addition or modification of an existing property that will exist on all objects.




## Recommendation

Update to version 4.17.11 or later.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2018-16487
- https://github.com/lodash/lodash/commit/90e6199a161b6445b01454517b40ef65ebecd2ad
- https://hackerone.com/reports/380873
- https://github.com/rubysec/ruby-advisory-db/blob/master/gems/lodash-rails/CVE-2018-16487.yml
- https://security.netapp.com/advisory/ntap-20190919-0004
