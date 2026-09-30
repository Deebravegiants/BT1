# [M] CVE-2026-44029

## Summary
Severity: Medium
Advisory: CVE-2026-44029
Aliases: GHSA-gr92-w2r5-qw5p
CVSS: 5.3 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:L/A:N)
Published: 2026-05-05
Source: https://osv.dev/vulnerability/CVE-2026-44029
Type: osv

## Details
An issue was discovered in Nix before 2.34.7. Writing to arbitrary files can occur via "nix-prefetch-url --unpack" or "nix store prefetch-file --unpack" directory traversal. The fixed versions are 2.34.7, 2.33.6, 2.32.8, 2.31.5, 2.30.5, 2.29.4, and 2.28.7 (introduced in 2.24.7);

## References
- https://www.openwall.com/lists/oss-security/2026/05/04/33
- https://discourse.nixos.org/t/security-advisory-local-privilege-escalation-in-lix-and-nix/77407
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/44xxx/CVE-2026-44029.json
- https://github.com/NixOS/nix/security/advisories/GHSA-gr92-w2r5-qw5p
- https://nvd.nist.gov/vuln/detail/CVE-2026-44029
