# [M] ROTP 6.2.2 and 6.2.1 has 0666 permissions for the .rb files.

## Summary
Severity: Medium
Advisory: GHSA-x2h8-qmj4-g62f
CVE: CVE-2024-28862
CWE: CWE-276
Ecosystem: RubyGems
CVSS: CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:L/I:L/A:L (CVSS_V3)
Published: 2024-03-18
Source: https://github.com/advisories/GHSA-x2h8-qmj4-g62f
Type: github-advisory

## Affected
- RubyGems: `rotp` — affected >=6.2.1 <6.3.0

## Details
The Ruby One Time Password library (ROTP) is an open source library for generating and validating one time passwords. Affected versions had overly permissive default permissions. Users should patch to version 6.3.0. Users unable to patch may correct file permissions after installation.

## References
- https://github.com/mdp/rotp/security/advisories/GHSA-x2h8-qmj4-g62f
- https://nvd.nist.gov/vuln/detail/CVE-2024-28862
- https://github.com/mdp/rotp
- https://github.com/rubysec/ruby-advisory-db/blob/master/gems/rotp/CVE-2024-28862.yml
