# [M] CVE-2024-36050

## Summary
Severity: Medium
Advisory: CVE-2024-36050
CVSS: 4.3 (CVSS:3.1/AV:N/AC:L/PR:N/UI:R/S:U/C:N/I:L/A:N)
Published: 2024-05-18
Source: https://osv.dev/vulnerability/CVE-2024-36050
Type: osv

## Details
Nix through 2.22.1 mishandles certain usage of hash caches, which makes it easier for attackers to replace current source code with attacker-controlled source code by luring a maintainer into accepting a malicious pull request.

## References
- https://discourse.nixos.org/t/nixpkgs-supply-chain-security-project/34345
- https://discourse.nixos.org/t/security-advisory-privilege-escalations-in-nix-lix-and-guix/66017/26
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2024/36xxx/CVE-2024-36050.json
- https://nvd.nist.gov/vuln/detail/CVE-2024-36050
- https://github.com/NixOS/nix/issues/969
- https://github.com/NixOS/ofborg/issues/68#issuecomment-2082789441
