# [H] Decidim amendments can be accepted or rejected by anyone

## Summary
Severity: High
Advisory: GHSA-w5xj-99cg-rccm
CVE: CVE-2026-40869
CWE: CWE-266
Ecosystem: RubyGems
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:H/A:N (CVSS_V3)
Published: 2026-04-14
Source: https://github.com/advisories/GHSA-w5xj-99cg-rccm
Type: github-advisory

## Affected
- RubyGems: `decidim-core` — affected >=0.31.0.rc1 <0.31.1
- RubyGems: `decidim-core` — affected >=0.19.0 <0.30.5

## Details
### Impact
The vulnerability allows any registered and authenticated user to accept or reject any amendments. The impact is on any users who have created proposals where the amendments feature is enabled. This also elevates the user accepting the amendment as the author of the original proposal as people amending proposals are provided coauthorship on the coauthorable resources.

The only check done when accepting or rejecting amendments is whether the amendment reactions are enabled for the component:
https://github.com/decidim/decidim/blob/9d6c3d2efe5a83bb02e095824ff5998d96a75eb7/decidim-core/app/permissions/decidim/permissions.rb#L107

The permission checks have been changed at 1b99136 which was introduced in released version 0.19.0. I have not investigated whether prior versions are also affected.

### Patches

Not available

### Workarounds
Disable amendment reactions for the amendable component (e.g. proposals).

## References
- https://github.com/decidim/decidim/security/advisories/GHSA-w5xj-99cg-rccm
- https://nvd.nist.gov/vuln/detail/CVE-2026-40869
- https://github.com/decidim/decidim/commit/1b99136a1c7aa02616a0b54a6ab88d12907a57a9
- https://github.com/decidim/decidim
- https://github.com/rubysec/ruby-advisory-db/blob/master/gems/decidim-core/CVE-2026-40869.yml
