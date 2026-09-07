# [M] Sisimai Inefficient Regular Expression Complexity vulnerability

## Summary
Severity: Medium
Advisory: GHSA-vm74-j4wq-82xj
CVE: CVE-2022-4891
CWE: CWE-1333
Ecosystem: RubyGems
CVSS: CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:N/I:N/A:L (CVSS_V3)
Published: 2023-01-17
Source: https://github.com/advisories/GHSA-vm74-j4wq-82xj
Type: github-advisory

## Affected
- RubyGems: `sisimai` — affected >=0 <4.25.14p12

## Details
A vulnerability has been found in Sisimai up to 4.25.14p11 and classified as problematic. This vulnerability affects the function `to_plain` of the file `lib/sisimai/string.rb`. The manipulation leads to inefficient regular expression complexity. The exploit has been disclosed to the public and may be used. Upgrading to version 4.25.14p12 is able to address this issue. The name of the patch is 51fe2e6521c9c02b421b383943dc9e4bbbe65d4e. It is recommended to upgrade the affected component. The identifier of this vulnerability is VDB-218452.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2022-4891
- https://github.com/sisimai/rb-sisimai/pull/244
- https://github.com/sisimai/rb-sisimai/commit/51fe2e6521c9c02b421b383943dc9e4bbbe65d4e
- https://gist.githubusercontent.com/gmcabrita/e5dc0332473fc2e3a7a407434c8d21c7/raw/00b12035e5e1b685469f143b94301a50306376ba/example.html
- https://github.com/rubysec/ruby-advisory-db/blob/master/gems/sisimai/CVE-2022-4891.yml
- https://github.com/sisimai/rb-sisimai
- https://github.com/sisimai/rb-sisimai/releases/tag/v4.25.14p12
- https://vuldb.com/?ctiid.218452
- https://vuldb.com/?id.218452
