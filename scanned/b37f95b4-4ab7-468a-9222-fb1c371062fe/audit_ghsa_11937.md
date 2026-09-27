# [M] Rails Active Storage has possible content type bypass via metadata in direct uploads

## Summary
Severity: Medium
Advisory: GHSA-qcfx-2mfw-w4cg
CVE: CVE-2026-33173
CWE: CWE-925
Ecosystem: RubyGems
CVSS: CVSS:4.0/AV:N/AC:L/AT:N/PR:N/UI:P/VC:N/VI:L/VA:N/SC:N/SI:N/SA:N (CVSS_V4)
Published: 2026-03-23
Source: https://github.com/advisories/GHSA-qcfx-2mfw-w4cg
Type: github-advisory

## Affected
- RubyGems: `activestorage` — affected >=8.1.0.beta1 <8.1.2.1
- RubyGems: `activestorage` — affected >=8.0.0.beta1 <8.0.4.1
- RubyGems: `activestorage` — affected >=0 <7.2.3.1

## Details
### Impact
Active Storage's `DirectUploadsController` accepts arbitrary metadata from the client and persists it on the blob. Because internal flags like `identified` and `analyzed` are stored in the same metadata hash, a malicious direct-upload client could set these flags.

### Releases
The fixed releases are available at the normal locations.

### Credit
This was responsible reported by Hackerone researcher [pwnie](https://hackerone.com/pwnie)

## References
- https://github.com/rails/rails/security/advisories/GHSA-qcfx-2mfw-w4cg
- https://nvd.nist.gov/vuln/detail/CVE-2026-33173
- https://github.com/rails/rails/commit/707c0f1f41f067fdf96d54e99d43b28dfaae7e53
- https://github.com/rails/rails/commit/8fcb934caadc79c8cc4ce53287046d0f67005b3e
- https://github.com/rails/rails/commit/d9502f5214e2198245a4c1defe9cd02a7c8057d0
- https://github.com/rails/rails
- https://github.com/rails/rails/releases/tag/v7.2.3.1
- https://github.com/rails/rails/releases/tag/v8.0.4.1
- https://github.com/rails/rails/releases/tag/v8.1.2.1
- https://github.com/rubysec/ruby-advisory-db/blob/master/gems/activestorage/CVE-2026-33173.yml
