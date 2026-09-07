# [H] Improper Certificate Validation in chloride

## Summary
Severity: High
Advisory: GHSA-573x-jhqh-jg36
CVE: CVE-2018-6517
CWE: CWE-295
Ecosystem: RubyGems
CVSS: CVSS:3.0/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:H/A:N (CVSS_V3)
Published: 2019-03-25
Source: https://github.com/advisories/GHSA-573x-jhqh-jg36
Type: github-advisory

## Affected
- RubyGems: `chloride` — affected >=0 <0.3.0

## Details
Prior to version 0.3.0, chloride's use of net-ssh resulted in host fingerprints for previously unknown hosts getting added to the user's known_hosts file without confirmation. In version 0.3.0 this is updated so that the user's known_hosts file is not updated by chloride.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2018-6517
- https://github.com/rubysec/ruby-advisory-db/blob/master/gems/chloride/CVE-2018-6517.yml
- https://puppet.com/security/cve/CVE-2018-6517
- https://web.archive.org/web/20201001014342/https://puppet.com/security/cve/CVE-2018-6517
