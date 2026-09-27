# [C] flash_tool Gem for Ruby File Download Handling Arbitrary Command Execution

## Summary
Severity: Critical
Advisory: GHSA-6325-6g32-7p35
CVE: CVE-2013-2513
CWE: CWE-77
Ecosystem: RubyGems
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H (CVSS_V3)
Published: 2023-01-26
Source: https://github.com/advisories/GHSA-6325-6g32-7p35
Type: github-advisory

## Affected
- RubyGems: `flash_tool` — affected >=0

## Details
flash_tool Gem for Ruby contains a flaw that is triggered during the handling of downloaded files that contain shell characters. With a specially crafted file, a context-dependent attacker can execute arbitrary commands.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2013-2513
- https://github.com/advisories/GHSA-6325-6g32-7p35
- https://github.com/milboj/flash_tool
- https://github.com/rubysec/ruby-advisory-db/blob/master/gems/flash_tool/CVE-2013-2513.yml
