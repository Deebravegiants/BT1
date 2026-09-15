# [C] Improper handling of double quotes in file name in Diffy in Windows environment

## Summary
Severity: Critical
Advisory: GHSA-5ww9-9qp2-x524
CVE: CVE-2022-33127
Ecosystem: RubyGems
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H (CVSS_V3)
Published: 2022-06-24
Source: https://github.com/advisories/GHSA-5ww9-9qp2-x524
Type: github-advisory

## Affected
- RubyGems: `diffy` — affected >=0 <3.4.1

## Details
The function that calls the diff tool in versions of Diffy prior to 3.4.1 does not properly handle double quotes in a filename when run in a Windows environment. This allows attackers to execute arbitrary commands via a crafted string.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2022-33127
- https://github.com/samg/diffy/commit/478f392082b66d38f54a02b4bb9c41be32fd6593
- https://github.com/rubysec/ruby-advisory-db/blob/master/gems/diffy/CVE-2022-33127.yml
- https://github.com/samg/diffy
- https://github.com/samg/diffy/blob/56fd935aea256742f7352b050592542d3d153bf6/CHANGELOG#L1
