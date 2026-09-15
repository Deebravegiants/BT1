# [H] Nix's privilege dropping to build user broke for macOS

## Summary
Severity: High
Advisory: CVE-2025-53819
Aliases: GHSA-qc7j-jgf3-qmhg
CVSS: 7.9 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:C/C:L/I:H/A:L)
Published: 2025-07-14
Source: https://osv.dev/vulnerability/CVE-2025-53819
Type: osv

## Details
Nix is a package manager for Linux and other Unix systems. Builds with Nix 2.30.0 on macOS were executed with elevated privileges (root), instead of the build users. The fix was applied to Nix 2.30.1. No known workarounds are available.

## References
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2025/53xxx/CVE-2025-53819.json
- https://github.com/NixOS/nix/security/advisories/GHSA-qc7j-jgf3-qmhg
- https://nvd.nist.gov/vuln/detail/CVE-2025-53819
- https://github.com/NixOS/nix/commit/e2ef2cfcbc83ea01308ee64c38a58707ab23dec3
- https://github.com/NixOS/nix/pull/13281
- https://github.com/NixOS/nix/pull/13455
