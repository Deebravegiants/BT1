# [M] Smashing Cross-site Scripting vulnerability

## Summary
Severity: Medium
Advisory: GHSA-254j-mmc5-qhpx
CVE: CVE-2021-35440
CWE: CWE-79
Ecosystem: RubyGems
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:R/S:C/C:L/I:L/A:N (CVSS_V3)
Published: 2022-05-24
Source: https://github.com/advisories/GHSA-254j-mmc5-qhpx
Type: github-advisory

## Affected
- RubyGems: `smashing` — affected >=0 <1.3.5

## Details
Smashing 1.3.4 is vulnerable to Cross Site Scripting (XSS). A URL for a widget can be crafted and used to execute JavaScript on the victim's computer. The JavaScript code can then steal data available in the session/cookies depending on the user environment (e.g. if re-using internal URL's for deploying, or cookies that are very permissive) private information may be retrieved by the attacker.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2021-35440
- https://github.com/Smashing/smashing/pull/186
- https://github.com/Smashing/smashing/pull/186/commits/f4648137ae77aa2a9ccd14b2e6eeaed2cfb32da3
- https://github.com/Smashing/smashing
- https://github.com/Smashing/smashing/blob/ad7325f159f89854ca4e7d94e7be9bee507b6d46/CHANGELOG.md
- https://github.com/rubysec/ruby-advisory-db/blob/master/gems/smashing/CVE-2021-35440.yml
