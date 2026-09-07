# [C] Slanger Arbitrary command execution

## Summary
Severity: Critical
Advisory: GHSA-rg32-m3hf-772v
CVE: CVE-2019-1010306
CWE: CWE-502
Ecosystem: RubyGems
CVSS: CVSS:3.0/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H (CVSS_V3)
Published: 2019-07-16
Source: https://github.com/advisories/GHSA-rg32-m3hf-772v
Type: github-advisory

## Affected
- RubyGems: `slanger` — affected >=0 <0.6.1

## Details
Slanger 0.6.0 is affected by Remote Code Execution (RCE). The impact is A remote attacker can execute arbitrary commands by sending a crafted request to the server. The component is Message handler & request validator. The attack vector is Remote unauthenticated. The fixed version is after commit 5267b455caeb2e055cccf0d2b6a22727c111f5c3.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2019-1010306
- https://github.com/stevegraham/slanger/pull/238
- https://github.com/stevegraham/slanger/pull/238/commits/5267b455caeb2e055cccf0d2b6a22727c111f5c3
- https://github.com/rubysec/ruby-advisory-db/blob/master/gems/slanger/CVE-2019-1010306.yml
- https://github.com/stevegraham/slanger
