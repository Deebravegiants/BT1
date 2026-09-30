# [M] Cryptomator: Unverified masterkeyfile key IDs can access arbitrary local or UNC paths

## Summary
Severity: Medium
Advisory: CVE-2026-32310
Aliases: GHSA-5phc-5pfx-hr52
CVSS: 4.1 (CVSS:3.1/AV:N/AC:L/PR:L/UI:R/S:C/C:L/I:N/A:N)
Published: 2026-03-20
Source: https://osv.dev/vulnerability/CVE-2026-32310
Type: osv

## Details
Cryptomator encrypts data being stored on cloud infrastructure. From version 1.6.0 to before version 1.19.1, vault configuration is parsed before its integrity is verified, and the masterkeyfile loader uses the unverified keyId as a filesystem path. The loader resolves keyId.getSchemeSpecificPart() directly against the vault path and immediately calls Files.exists(...). This allows a malicious vault config to supply parent-directory escapes, absolute local paths, or UNC paths (e.g., masterkeyfile://attacker/share/masterkey.cryptomator). On Windows, the UNC variant is especially dangerous because Path.resolve("//attacker/share/...") becomes \\attacker\share\..., so the existence check can trigger outbound SMB access before the user even enters a passphrase. This issue has been patched in version 1.19.1.

## References
- https://github.com/cryptomator/cryptomator/releases/tag/1.19.1
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/32xxx/CVE-2026-32310.json
- https://github.com/cryptomator/cryptomator/security/advisories/GHSA-5phc-5pfx-hr52
- https://nvd.nist.gov/vuln/detail/CVE-2026-32310
- https://github.com/cryptomator/cryptomator/commit/1e3dfe3de1623b1b85d24db91e49d31d1ea11f40
- https://github.com/cryptomator/cryptomator/pull/4180
