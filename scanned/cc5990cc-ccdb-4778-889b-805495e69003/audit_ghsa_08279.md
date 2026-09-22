# [H] katalyst-koi: Session cookies can be replayed after user logout

## Summary
Severity: High
Advisory: GHSA-4cx3-3c38-j9vv
CVE: CVE-2026-44511
CWE: CWE-613
Ecosystem: RubyGems
CVSS: CVSS:3.1/AV:N/AC:H/PR:N/UI:N/S:U/C:H/I:H/A:N (CVSS_V3)
Published: 2026-05-07
Source: https://github.com/advisories/GHSA-4cx3-3c38-j9vv
Type: github-advisory

## Affected
- RubyGems: `katalyst-koi` — affected >=0 <4.20.0
- RubyGems: `katalyst-koi` — affected >=5.0.0 <5.6.0

## Details
### Impact

Admin session cookies were not invalidated when an admin user logged out. An attacker with access to a valid admin session cookie could continue to access admin functionality after logout, until the cookie expired or session secrets were rotated.

This affects applications using Koi admin authentication where an admin session cookie may have been exposed, cached, intercepted, or otherwise retained after logout.

### Patches

The issue has been patched by recording admin logout time and rejecting any admin session cookie created before the user’s most recent logout.

Users should upgrade to the patched Koi releases once available.

### Workarounds

Katalyst Koi recommends upgrading to the latest available version, or back porting the changes released in 5.6.0/4.20.0

### Resources

This is an application of https://guides.rubyonrails.org/v5.2.0/security.html#replay-attacks-for-cookiestore-sessions

## References
- https://github.com/katalyst/koi/security/advisories/GHSA-4cx3-3c38-j9vv
- https://nvd.nist.gov/vuln/detail/CVE-2026-44511
- https://github.com/katalyst/koi
- https://github.com/rubysec/ruby-advisory-db/blob/master/gems/katalyst-koi/CVE-2026-44511.yml
- https://guides.rubyonrails.org/v5.2.0/security.html#replay-attacks-for-cookiestore-sessions
