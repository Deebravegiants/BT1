# [M] Inline SVG vulnerable to Cross-site Scripting

## Summary
Severity: Medium
Advisory: GHSA-p33q-4h4m-j994
CVE: CVE-2020-36644
CWE: CWE-79
Ecosystem: RubyGems
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:R/S:C/C:L/I:L/A:N (CVSS_V3)
Published: 2023-01-07
Source: https://github.com/advisories/GHSA-p33q-4h4m-j994
Type: github-advisory

## Affected
- RubyGems: `inline_svg` — affected >=0 <1.7.2

## Details
A vulnerability has been found in jamesmartin Inline SVG up to 1.7.1 and classified as problematic. Affected by this vulnerability is an unknown functionality of the file `lib/inline_svg/action_view/helpers.rb` of the component `URL Parameter Handler`. The manipulation of the argument filename leads to cross site scripting. The attack can be launched remotely. Upgrading to version 1.7.2 is able to address this issue. The name of the patch is f5363b351508486021f99e083c92068cf2943621. It is recommended to upgrade the affected component. The identifier VDB-217597 was assigned to this vulnerability.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2020-36644
- https://github.com/jamesmartin/inline_svg/pull/117
- https://github.com/jamesmartin/inline_svg/commit/f5363b351508486021f99e083c92068cf2943621
- https://github.com/jamesmartin/inline_svg
- https://github.com/jamesmartin/inline_svg/releases/tag/v1.7.2
- https://github.com/rubysec/ruby-advisory-db/blob/master/gems/inline_svg/CVE-2020-36644.yml
- https://vuldb.com/?ctiid.217597
- https://vuldb.com/?id.217597
