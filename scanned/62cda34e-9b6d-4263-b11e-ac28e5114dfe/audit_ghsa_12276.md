# [C] Safemode Gem Has Incomplete List of Disallowed Inputs

## Summary
Severity: Critical
Advisory: GHSA-5vx5-9q73-wgp4
CVE: CVE-2017-7540
CWE: CWE-184
Ecosystem: RubyGems
CVSS: CVSS:3.0/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H (CVSS_V3)
Published: 2017-10-24
Source: https://github.com/advisories/GHSA-5vx5-9q73-wgp4
Type: github-advisory

## Affected
- RubyGems: `safemode` — affected >=0 <1.3.2

## Details
rubygem-safemode, as used in Foreman, versions 1.3.1 and earlier are vulnerable to bypassing safe mode limitations via special Ruby syntax. This can lead to deletion of objects for which the user does not have delete permissions or possibly to privilege escalation.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2017-7540
- https://github.com/svenfuchs/safemode/pull/23
- https://github.com/rubysec/ruby-advisory-db/blob/master/gems/safemode/CVE-2017-7540.yml
- https://github.com/svenfuchs/safemode
