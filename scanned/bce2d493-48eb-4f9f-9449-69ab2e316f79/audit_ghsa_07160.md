# [M] Sharp Missing Authorization Check in Quick Creation Command Endpoints

## Summary
Severity: Medium
Advisory: GHSA-vmwx-m75v-qvch
CVE: CVE-2026-53634
CWE: CWE-862
Ecosystem: Packagist
CVSS: CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:N/I:L/A:N (CVSS_V3)
Published: 2026-07-08
Source: https://github.com/advisories/GHSA-vmwx-m75v-qvch
Type: github-advisory

## Affected
- Packagist: `code16/sharp` — affected >=9.0.0 <9.22.3

## Details
### Impact
The create and store endpoints of the Quick Creation Command feature did not enforce any authorization check. An authenticated Sharp user without create permission on a given entity could bypass the authorization layer and either retrieve the creation form or submit new records for that entity, as long as it had a Quick Creation Command handler configured.

### Patches
Yes. The fix is included in version 9.22.3. Users should upgrade to that version or later.

### Workarounds
Remove or disable Quick Creation Command handlers (quickCreationCommandHandler()) on any entity list where unauthorized access is a concern, until an upgrade is possible.

### Resources
[PR #729](https://github.com/code16/sharp/pull/729)

## References
- https://github.com/code16/sharp/security/advisories/GHSA-vmwx-m75v-qvch
- https://nvd.nist.gov/vuln/detail/CVE-2026-53634
- https://github.com/code16/sharp/pull/729
- https://github.com/code16/sharp/commit/aa18a85fd8fef830988a336cad2278986729d21a
- https://github.com/code16/sharp
- https://github.com/code16/sharp/releases/tag/v9.22.3
