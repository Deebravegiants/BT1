# [H] CVE-2026-44028

## Summary
Severity: High
Advisory: CVE-2026-44028
Aliases: GHSA-vh5x-56v6-4368
CVSS: 7.5 (CVSS:3.1/AV:L/AC:H/PR:L/UI:N/S:C/C:H/I:H/A:N)
Published: 2026-05-05
Source: https://osv.dev/vulnerability/CVE-2026-44028
Type: osv

## Details
An issue was discovered in Nix before 2.34.7 and Lix before 2.95.2. Unbounded recursion in the NAR (Nix Archive) parser could lead to a stack-to-heap overflow when the parser is run on a coroutine stack. The stack is allocated without a guard page, which means that a stack overflow could overwrite memory on the heap and could allow arbitrary code execution as the Nix daemon (run as root in multi-user installations) if ASLR hardening is bypassed. This can be exploited by all users able to connect to the daemon (e.g., in Nix, this is configurable via the allowed-users setting, defaulting to all users). The fixed versions are 2.34.7, 2.33.6, 2.32.8, 2.31.5, 2.30.5, 2.29.4, and 2.28.7 for Nix (introduced in 2.24.4); and 2.95.2, 2.94.2, and 2.93.4 for Lix (introduced in 2.93.0).

## References
- https://www.openwall.com/lists/oss-security/2026/05/04/32
- https://www.openwall.com/lists/oss-security/2026/05/04/33
- https://discourse.nixos.org/t/security-advisory-local-privilege-escalation-in-lix-and-nix/77407
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/44xxx/CVE-2026-44028.json
- https://github.com/NixOS/nix/security/advisories/GHSA-vh5x-56v6-4368
- https://nvd.nist.gov/vuln/detail/CVE-2026-44028
- https://lix.systems/blog/2026-05-05-lix-unsigned-integer-overflow/
