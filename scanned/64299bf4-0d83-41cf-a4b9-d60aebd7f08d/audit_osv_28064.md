# [M] Nix Corruption of fixed-output derivations

## Summary
Severity: Medium
Advisory: CVE-2024-27297
Aliases: GHSA-2ffj-w4mj-pg37
CVSS: 6.3 (CVSS:3.1/AV:A/AC:L/PR:L/UI:N/S:U/C:N/I:H/A:L)
Published: 2024-03-11
Source: https://osv.dev/vulnerability/CVE-2024-27297
Type: osv

## Details
Nix is a package manager for Linux and other Unix systems. A fixed-output derivations on Linux can send file descriptors to files in the Nix store to another program running on the host (or another fixed-output derivation) via Unix domain sockets in the abstract namespace. This allows to modify the output of the derivation, after Nix has registered the path as "valid" and immutable in the Nix database. In particular, this allows the output of fixed-output derivations to be modified from their expected content. This issue has been addressed in versions 2.3.18 2.18.2 2.19.4 and 2.20.5. Users are advised to upgrade. There are no known workarounds for this vulnerability.

## References
- https://hackmd.io/03UGerewRcy3db44JQoWvw
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2024/27xxx/CVE-2024-27297.json
- https://github.com/NixOS/nix/security/advisories/GHSA-2ffj-w4mj-pg37
- https://nvd.nist.gov/vuln/detail/CVE-2024-27297
- https://github.com/NixOS/nix/commit/f8170ce9f119e5e6724eb81ff1b5a2d4c0024000
- https://guix.gnu.org/en/blog/2025/privilege-escalation-vulnerabilities-2025/
