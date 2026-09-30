# [H] Prototype Pollution in lodash

## Summary
Severity: High
Advisory: GHSA-p6mc-m468-83gw
CVE: CVE-2020-8203
CWE: CWE-1321, CWE-770
Ecosystem: RubyGems, npm
CVSS: CVSS:3.1/AV:N/AC:H/PR:N/UI:N/S:U/C:N/I:H/A:H (CVSS_V3)
Published: 2020-07-15
Source: https://github.com/advisories/GHSA-p6mc-m468-83gw
Type: github-advisory

## Affected
- npm: `lodash` — affected >=3.7.0 <4.17.19
- npm: `lodash-es` — affected >=3.7.0 <4.17.20
- npm: `lodash.pick` — affected >=4.0.0
- npm: `lodash.set` — affected >=3.7.0
- npm: `lodash.setwith` — affected >=0
- npm: `lodash.update` — affected >=0
- npm: `lodash.updatewith` — affected >=0
- RubyGems: `lodash-rails` — affected >=3.7.0 <4.17.19

## Details
Versions of lodash prior to 4.17.19 are vulnerable to Prototype Pollution. The functions `pick`, `set`, `setWith`, `update`, `updateWith`, and `zipObjectDeep` allow a malicious user to modify the prototype of Object if the property identifiers are user-supplied. Being affected by this issue requires manipulating objects based on user-provided property values or arrays.

This vulnerability causes the addition or modification of an existing property that will exist on all objects and may lead to Denial of Service or Code Execution under specific circumstances.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2020-8203
- https://github.com/lodash/lodash/issues/4744
- https://github.com/lodash/lodash/issues/4874
- https://github.com/github/advisory-database/pull/2884
- https://github.com/lodash/lodash/commit/c84fe82760fb2d3e03a63379b297a1cc1a2fce12
- https://hackerone.com/reports/712065
- https://hackerone.com/reports/864701
- https://github.com/lodash/lodash
- https://github.com/lodash/lodash/wiki/Changelog#v41719
- https://github.com/rubysec/ruby-advisory-db/blob/master/gems/lodash-rails/CVE-2020-8203.yml
- https://security.netapp.com/advisory/ntap-20200724-0006
- https://web.archive.org/web/20210914001339/https://github.com/lodash/lodash/issues/4744
