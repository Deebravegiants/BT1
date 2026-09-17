# [M] text_helpers uses web link to untrusted target with window.opener access

## Summary
Severity: Medium
Advisory: GHSA-74hc-57m5-83ch
CVE: CVE-2020-36624
CWE: CWE-1022, CWE-266
Ecosystem: RubyGems
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:R/S:C/C:L/I:L/A:N (CVSS_V3)
Published: 2022-12-22
Source: https://github.com/advisories/GHSA-74hc-57m5-83ch
Type: github-advisory

## Affected
- RubyGems: `text_helpers` — affected >=1.1.0 <1.2.0

## Details
A vulnerability was found in ahorner text-helpers 1.1.0/1.1.1. This vulnerability affects unknown code of the file lib/text_helpers/translation.rb. The manipulation of the argument link leads to use of web link to untrusted target with window.opener access. The attack can be initiated remotely. Upgrading to version 1.2.0 can address this issue. The name of the patch is 184b60ded0e43c985788582aca2d1e746f9405a3. It is recommended to upgrade the affected component. The identifier of this vulnerability is VDB-216520.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2020-36624
- https://github.com/ahorner/text-helpers/pull/19
- https://github.com/ahorner/text-helpers/commit/184b60ded0e43c985788582aca2d1e746f9405a3
- https://github.com/ahorner/text-helpers
- https://github.com/ahorner/text-helpers/releases/tag/v1.1.0
- https://github.com/ahorner/text-helpers/releases/tag/v1.2.0
- https://github.com/rubysec/ruby-advisory-db/blob/master/gems/text_helpers/CVE-2020-36624.yml
- https://vuldb.com/?id.216520
