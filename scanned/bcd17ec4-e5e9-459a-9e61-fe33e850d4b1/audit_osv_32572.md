# [H] Local privilege escalation in make-initrd-ng

## Summary
Severity: High
Advisory: CVE-2025-32438
Aliases: GHSA-m7pq-h9p4-8rr4
CVSS: 8.8 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:C/C:H/I:H/A:H)
Published: 2025-04-15
Source: https://osv.dev/vulnerability/CVE-2025-32438
Type: osv

## Details
make-initrd-ng is a tool for copying binaries and their dependencies. Local privilege escalation affecting all NixOS users. With systemd.shutdownRamfs.enable enabled (the default) a local user is able to create a program that will be executed by root during shutdown. Patches exist for NixOS 24.11 and 25.05 / unstable. As a workaround, set systemd.shutdownRamfs.enable = false;.

## References
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2025/32xxx/CVE-2025-32438.json
- https://github.com/NixOS/nixpkgs/security/advisories/GHSA-m7pq-h9p4-8rr4
- https://nvd.nist.gov/vuln/detail/CVE-2025-32438
- https://github.com/NixOS/nixpkgs/commit/b17590193d8e5697000c23c66afcf11e1753734d
- https://github.com/NixOS/nixpkgs/commit/fbf76bf72b161b9f4ab97704a8258776d5f3ffba
