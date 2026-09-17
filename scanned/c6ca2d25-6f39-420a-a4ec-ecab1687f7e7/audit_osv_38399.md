# [C] Nix sandbox escape: file write via symlink at FOD `.tmp` copy destination

## Summary
Severity: Critical
Advisory: CVE-2026-39860
Aliases: GHSA-g3g9-5vj6-r3gj
CVSS: 9.0 (CVSS:3.1/AV:L/AC:L/PR:N/UI:N/S:C/C:H/I:H/A:N)
Published: 2026-04-08
Source: https://osv.dev/vulnerability/CVE-2026-39860
Type: osv

## Details
Nix is a package manager for Linux and other Unix systems. A bug in the fix for CVE-2024-27297 allowed for arbitrary overwrites of files writable by the Nix process orchestrating the builds (typically the Nix daemon running as root in multi-user installations) by following symlinks during fixed-output derivation output registration. This affects sandboxed Linux builds - sandboxed macOS builds are unaffected. The location of the temporary output used for the output copy was located inside the build chroot. A symlink, pointing to an arbitrary location in the filesystem, could be created by the derivation builder at that path. During output registration, the Nix process (running in the host mount namespace) would follow that symlink and overwrite the destination with the derivation's output contents. In multi-user installations, this allows all users able to submit builds to the Nix daemon (allowed-users - defaulting to all users) to gain root privileges by modifying sensitive files. This vulnerability is fixed in 2.34.5, 2.33.4, 2.32.7, 2.31.4, 2.30.4, 2.29.3, and 2.28.6.

## References
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/39xxx/CVE-2026-39860.json
- https://github.com/NixOS/nix/security/advisories/GHSA-g3g9-5vj6-r3gj
- https://nvd.nist.gov/vuln/detail/CVE-2026-39860
- https://github.com/NixOS/nix/commit/244f3eee0bbc7f11e9b383a15ed7368e2c4becc9
- https://github.com/NixOS/nix/commit/4bc5a3510fa3735798f9ed3a2a30a3ea7b32343a
- https://github.com/NixOS/nix/commit/7794354a982449927ee7401cdeb573ddd16c4688
- https://github.com/NixOS/nix/commit/a3163b9eabb952b4aa96e376dea95ebcca97b31a
- https://github.com/NixOS/nix/pull/10178
