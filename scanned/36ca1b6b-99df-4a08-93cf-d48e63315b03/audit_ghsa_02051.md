# [C] Dragonfly contains remote code execution vulnerability

## Summary
Severity: Critical
Advisory: GHSA-j858-xp5v-f8xx
CVE: CVE-2021-33564
CWE: CWE-88, CWE-94
Ecosystem: RubyGems
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H (CVSS_V3)
Published: 2021-06-02
Source: https://github.com/advisories/GHSA-j858-xp5v-f8xx
Type: github-advisory

## Affected
- RubyGems: `dragonfly` — affected >=0 <1.4.0

## Details
An argument injection vulnerability in the Dragonfly gem before 1.4.0 for Ruby allows remote attackers to read and write to arbitrary files via a crafted URL when the `verify_url` option is disabled. This may lead to code execution. The problem occurs because the generate and process features mishandle use of the ImageMagick convert utility.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2021-33564
- https://github.com/markevans/dragonfly/issues/513
- https://github.com/markevans/dragonfly/commit/25399297bb457f7fcf8e3f91e85945b255b111b5
- https://github.com/advisories/GHSA-j858-xp5v-f8xx
- https://github.com/markevans/dragonfly/compare/v1.3.0...v1.4.0
- https://github.com/mlr0p/CVE-2021-33564
- https://github.com/rubysec/ruby-advisory-db/blob/master/gems/dragonfly/CVE-2021-33564.yml
- https://raw.githubusercontent.com/projectdiscovery/nuclei-templates/master/cves/2021/CVE-2021-33564.yaml
- https://zxsecurity.co.nz/research/argunment-injection-ruby-dragonfly
