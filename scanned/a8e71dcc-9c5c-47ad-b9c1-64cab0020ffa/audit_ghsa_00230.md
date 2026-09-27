# [M] Prototype Pollution in lodash

## Summary
Severity: Medium
Advisory: GHSA-fvqr-27wr-82fm
CVE: CVE-2018-3721
CWE: CWE-1321, CWE-471
Ecosystem: RubyGems, npm
CVSS: CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:N/I:H/A:N (CVSS_V3)
Published: 2018-07-26
Source: https://github.com/advisories/GHSA-fvqr-27wr-82fm
Type: github-advisory

## Affected
- npm: `lodash` — affected >=0 <4.17.5
- RubyGems: `lodash-rails` — affected >=0 <4.17.5

## Details
Versions of `lodash` before 4.17.5 are vulnerable to prototype pollution. 

The vulnerable functions are 'defaultsDeep', 'merge', and 'mergeWith' which allow a malicious user to modify the prototype of `Object` via `__proto__` causing the addition or modification of an existing property that will exist on all objects.




## Recommendation

Update to version 4.17.5 or later.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2018-3721
- https://github.com/lodash/lodash/commit/d8e069cc3410082e44eb18fcf8e7f3d08ebe1d4a
- https://hackerone.com/reports/310443
- https://github.com/rubysec/ruby-advisory-db/blob/master/gems/lodash-rails/CVE-2018-3721.yml
- https://security.netapp.com/advisory/ntap-20190919-0004
