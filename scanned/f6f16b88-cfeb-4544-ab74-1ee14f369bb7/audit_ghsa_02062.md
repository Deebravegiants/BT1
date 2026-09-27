# [M] Automatic room upgrade handling can be used maliciously to bridge a room non-consentually 

## Summary
Severity: Medium
Advisory: GHSA-35g4-qx3c-vjhx
CVE: CVE-2021-32659
CWE: CWE-306
Ecosystem: npm
CVSS: CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:H/I:N/A:N (CVSS_V3)
Published: 2021-06-21
Source: https://github.com/advisories/GHSA-35g4-qx3c-vjhx
Type: github-advisory

## Affected
- npm: `matrix-appservice-bridge` — affected >=0 <2.6.1

## Details
### Impact

If a bridge has room upgrade handling turned on in the configuration (the `roomUpgradeOpts` key when instantiating a new `Bridge` instance.), any `m.room.tombstone` event it encounters will be used to unbridge the current room and bridge into the target room. However, the target room `m.room.create` event is not checked to verify if the `predecessor` field contains the previous room. This means that any mailcious admin of a bridged room can repoint the traffic to a different room without the new room being aware.


### Patches

Versions 2.6.1 and greater are patched.

### Workarounds

Disabling the automatic room upgrade handling can be done by removing the `roomUpgradeOpts` key from the `Bridge` class options. 

### References

The issue is patched by https://github.com/matrix-org/matrix-appservice-bridge/pull/330

### For more information]

If you have any questions or comments about this advisory, email us at security@matrix.org.

## References
- https://github.com/matrix-org/matrix-appservice-bridge/security/advisories/GHSA-35g4-qx3c-vjhx
- https://nvd.nist.gov/vuln/detail/CVE-2021-32659
- https://github.com/matrix-org/matrix-appservice-bridge/pull/330
- https://github.com/matrix-org/matrix-appservice-bridge/commit/b69e745584a34fcfd858df33e4631e420da07b9f
- https://github.com/matrix-org/matrix-appservice-bridge/releases/tag/2.6.1
