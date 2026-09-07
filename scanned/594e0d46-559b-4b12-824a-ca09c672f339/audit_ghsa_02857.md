# [C] Remote code execution in ruby-jss

## Summary
Severity: Critical
Advisory: GHSA-vmfh-c547-v45h
CVE: CVE-2021-33575
Ecosystem: RubyGems
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H (CVSS_V3)
Published: 2021-10-06
Source: https://github.com/advisories/GHSA-vmfh-c547-v45h
Type: github-advisory

## Affected
- RubyGems: `ruby-jss` — affected >=0 <1.6.0

## Details
The Pixar ruby-jss gem before 1.6.0 allows remote attackers to execute arbitrary code because of the Plist gem's documented behavior of using Marshal.load during XML document processing.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2021-33575
- https://github.com/PixarAnimationStudios/ruby-jss
- https://github.com/PixarAnimationStudios/ruby-jss/blob/e6d48dd8c77f9275c76787d60d3472615fcd9b77/CHANGES.md#160---2021-05-24
- https://github.com/advisories/GHSA-vmfh-c547-v45h
- https://github.com/patsplat/plist/tree/ce8f9ae42a114f603ea200c955e420782bffc4ad#label-Security+considerations
- https://github.com/rubysec/ruby-advisory-db/blob/master/gems/ruby-jss/CVE-2021-33575.yml
