# [M] Oxidized Web vulnerable to Cross-site Scripting

## Summary
Severity: Medium
Advisory: GHSA-8qwh-rm6c-jv96
CVE: CVE-2019-25088
CWE: CWE-79
Ecosystem: RubyGems
CVSS: CVSS:3.1/AV:N/AC:L/PR:L/UI:R/S:C/C:L/I:L/A:N (CVSS_V3)
Published: 2022-12-27
Source: https://github.com/advisories/GHSA-8qwh-rm6c-jv96
Type: github-advisory

## Affected
- RubyGems: `oxidized-web` — affected >=0

## Details
A vulnerability was found in ytti Oxidized Web. It has been classified as problematic. Affected is an unknown function of the file `lib/oxidized/web/views/conf_search.haml`. The manipulation of the argument `to_research` leads to cross site scripting. It is possible to launch the attack remotely. The name of the patch is 55ab9bdc68b03ebce9280b8746ef31d7fdedcc45. It is recommended to apply a patch to fix this issue. VDB-216870 is the identifier assigned to this vulnerability.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2019-25088
- https://github.com/ytti/oxidized-web/pull/195
- https://github.com/ytti/oxidized-web/commit/55ab9bdc68b03ebce9280b8746ef31d7fdedcc45
- https://github.com/rubysec/ruby-advisory-db/blob/master/gems/oxidized-web/CVE-2019-25088.yml
- https://github.com/ytti/oxidized-web
- https://vuldb.com/?ctiid.216870
- https://vuldb.com/?id.216870
