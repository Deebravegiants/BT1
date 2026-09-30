# [M] BigBlueButton contains Response leaks in anonymous polls

## Summary
Severity: Medium
Advisory: CVE-2022-41964
Aliases: GHSA-fgmj-rx7j-fqr4
CVSS: 5.7 (CVSS:3.1/AV:N/AC:L/PR:L/UI:R/S:U/C:H/I:N/A:N)
Published: 2022-12-16
Source: https://osv.dev/vulnerability/CVE-2022-41964
Type: osv

## Details
BigBlueButton is an open source web conferencing system. This vulnerability only affects release candidates of BigBlueButton 2.4. The attacker can start a subscription for poll results before starting an anonymous poll, and use this subscription to see individual responses in the anonymous poll. The attacker had to be a meeting presenter. This issue is patched in version 2.4.0. There are no workarounds.

## References
- https://github.com/bigbluebutton/bigbluebutton/releases/tag/v2.4.0
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2022/41xxx/CVE-2022-41964.json
- https://github.com/bigbluebutton/bigbluebutton/security/advisories/GHSA-fgmj-rx7j-fqr4
- https://nvd.nist.gov/vuln/detail/CVE-2022-41964
