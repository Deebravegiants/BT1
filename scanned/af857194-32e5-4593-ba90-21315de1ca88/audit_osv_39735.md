# [M] ClearanceKit: Policy signing key in System Keychain has permissive ACL allowing any local-root process to forge signed policy

## Summary
Severity: Medium
Advisory: CVE-2026-47134
Aliases: GHSA-w254-hxm5-3hgh
CVSS: 6.0 (CVSS:4.0/AV:L/AC:L/AT:P/PR:H/UI:N/VC:N/VI:H/VA:N/SC:H/SI:H/SA:N)
Published: 2026-07-20
Source: https://osv.dev/vulnerability/CVE-2026-47134
Type: osv

## Details
ClearanceKit intercepts file-system access events on macOS and enforces per-process access policies. The ECDSA private key used to sign the on-disk policy database (`/Library/Application Support/clearancekit/store.db`) is stored in the macOS System Keychain. The key was created via the two-step pattern `SecKeyCreateRandomKey` (in-memory) followed by `SecItemAdd(kSecValueRef:, kSecAttrAccess:)` (persist). Prior to version 5.0.10, for `kSecClassKey` items in the legacy System Keychain, `kSecAttrAccess` passed to `SecItemAdd` is silently ignored — the persisted key inherits no ACL restriction. The same access builder applied to `kSecClassGenericPassword` items correctly binds the ACL, making this bug specific to the EC key. The result is that any process running as root can use the key to produce valid signatures over arbitrary policy content. Version 5.0.10 fixes the issue. No known workarounds are available. Disabling the system extension and manually removing the System Keychain item labelled `clearancekit policy signing key` would prevent the forged-signature path but also disables policy enforcement.

## References
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/47xxx/CVE-2026-47134.json
- https://github.com/craigjbass/clearancekit/security/advisories/GHSA-w254-hxm5-3hgh
- https://nvd.nist.gov/vuln/detail/CVE-2026-47134
