# [C] Prototype Pollution in lodash

## Summary
Severity: Critical
Advisory: GHSA-jf85-cpcp-j695
CVE: CVE-2019-10744
CWE: CWE-1321, CWE-20
Ecosystem: RubyGems, npm
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:H/A:H (CVSS_V3)
Published: 2019-07-10
Source: https://github.com/advisories/GHSA-jf85-cpcp-j695
Type: github-advisory

## Affected
- npm: `lodash` — affected >=0 <4.17.12
- npm: `lodash-es` — affected >=0 <4.17.14
- npm: `lodash-amd` — affected >=0 <4.17.13
- npm: `lodash.defaultsdeep` — affected >=0 <4.6.1
- RubyGems: `lodash-rails` — affected >=0 <4.17.12

## Details
Versions of `lodash` before 4.17.12 are vulnerable to Prototype Pollution.  The function `defaultsDeep` allows a malicious user to modify the prototype of `Object` via `{constructor: {prototype: {...}}}` causing the addition or modification of an existing property that will exist on all objects.

## Recommendation

Update to version 4.17.12 or later.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2019-10744
- https://github.com/lodash/lodash/pull/4336
- https://access.redhat.com/errata/RHSA-2019:3024
- https://github.com/rubysec/ruby-advisory-db/blob/master/gems/lodash-rails/CVE-2019-10744.yml
- https://security.netapp.com/advisory/ntap-20191004-0005
- https://snyk.io/vuln/SNYK-JS-LODASH-450202
- https://support.f5.com/csp/article/K47105354?utm_source=f5support&amp%3Butm_medium=RSS
- https://support.f5.com/csp/article/K47105354?utm_source=f5support&amp;utm_medium=RSS
- https://www.oracle.com/security-alerts/cpujan2021.html
- https://www.oracle.com/security-alerts/cpuoct2020.html
