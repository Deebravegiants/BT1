# [H] CVE-2021-43814

## Summary
Severity: High
Advisory: CVE-2021-43814
Aliases: GHSA-hqqp-vjcm-mw8r
CVSS: 7.8 (CVSS:3.1/AV:L/AC:L/PR:N/UI:R/S:U/C:H/I:H/A:H)
Published: 2021-12-13
Source: https://osv.dev/vulnerability/CVE-2021-43814
Type: osv

## Details
Rizin is a UNIX-like reverse engineering framework and command-line toolset. In versions up to and including 0.3.1 there is a heap-based out of bounds write in parse_die() when reversing an AMD64 ELF binary with DWARF debug info. When a malicious AMD64 ELF binary is opened by a victim user, Rizin may crash or execute unintended actions. No workaround are known and users are advised to upgrade.

## References
- https://github.com/rizinorg/rizin/issues/2083
- https://github.com/rizinorg/rizin/security/advisories/GHSA-hqqp-vjcm-mw8r
- https://github.com/rizinorg/rizin/commit/aa6917772d2f32e5a7daab25a46c72df0b5ea406
