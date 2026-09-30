# [M] frost-core: refresh shares with smaller min_signers will reduce security of group

## Summary
Severity: Medium
Advisory: GHSA-wgq8-vr6r-mqxm
CVE: CVE-2025-58359
CWE: CWE-269, CWE-325
Ecosystem: crates.io
CVSS: CVSS:4.0/AV:N/AC:L/AT:P/PR:L/UI:N/VC:H/VI:N/VA:N/SC:N/SI:N/SA:N (CVSS_V4)
Published: 2025-09-03
Source: https://github.com/advisories/GHSA-wgq8-vr6r-mqxm
Type: github-advisory

## Affected
- crates.io: `frost-core` — affected >=2.0.0 <2.2.0

## Details
### Impact

It was not clear that it is not possible to change `min_signers` (i.e. the threshold) with the refresh share functionality (`frost_core::keys::refresh` module). Using a smaller value would not decrease the threshold, and attempts to sign using a smaller threshold would fail. Additionally, after refreshing the shares with a smaller threshold, it would still be possible to sign with the original threshold; however, this could cause a security loss to the participant's shares. We have not determined the exact security implications of doing so and judged simpler to just validate `min_signers`. 

 If for some reason you have done a refresh share procedure with a smaller `min_signers` we strongly recommend migrating to a new key. 

### Patches

Updating to 2.2.0 will ensure that the `min_signers` parameter will be validated. However it won't restore the security of groups refreshed with a smaller `min_signers` parameters.

### Workarounds

You don't need to update if you don't use the refresh share functionality, or if you didn't try to change the `min_signers` parameter using the refresh share functionality.

### References

Thank you [BlockSec](https://blocksec.com/) for reporting the finding

## References
- https://github.com/ZcashFoundation/frost/security/advisories/GHSA-wgq8-vr6r-mqxm
- https://nvd.nist.gov/vuln/detail/CVE-2025-58359
- https://github.com/ZcashFoundation/frost/commit/379ef689c733b3d9c80fd409071d4f3af4dafed2
- https://github.com/ZcashFoundation/frost
- https://github.com/ZcashFoundation/frost/releases/tag/frost-core%2Fv2.2.0
