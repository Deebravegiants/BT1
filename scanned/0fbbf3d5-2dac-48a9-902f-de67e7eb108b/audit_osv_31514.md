# [M] RNP 0.18.0 Vulnerable PKESK session keys

## Summary
Severity: Medium
Advisory: CVE-2025-13470
CVSS: 6.0 (CVSS:4.0/AV:N/AC:L/AT:N/PR:N/UI:N/VC:H/VI:N/VA:N/SC:N/SI:N/SA:N/E:P/AU:Y/RE:H/U:Red)
Published: 2025-11-21
Source: https://osv.dev/vulnerability/CVE-2025-13470
Type: osv

## Details
In RNP version 0.18.0 a refactoring regression causes the symmetric 
session key used for Public-Key Encrypted Session Key (PKESK) packets to
 be left uninitialized except for zeroing, resulting in it always being 
an all-zero byte array.

Any data encrypted using public-key encryption 
in this release can be decrypted trivially by supplying an all-zero 
session key, fully compromising confidentiality.

The vulnerability affects only public key encryption (PKESK packets).  Passphrase-based encryption (SKESK packets) is not affected.

Root cause: Vulnerable session key buffer used in PKESK packet generation.



The defect was introduced in commit `7bd9a8dc356aae756b40755be76d36205b6b161a` where initialization 
logic inside `encrypted_build_skesk()` only randomized the key for the 
SKESK path and omitted it for the PKESK path.

## References
- https://aur.archlinux.org/packages/rnp
- https://launchpad.net/ubuntu/+source/rnp
- https://packages.gentoo.org/packages/dev-util/librnp
- https://access.redhat.com/security/cve/cve-2025-13402
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2025/13xxx/CVE-2025-13470.json
- https://github.com/rnpgp/rnp/releases/tag/v0.18.1
- https://nvd.nist.gov/vuln/detail/CVE-2025-13470
- https://open.ribose.com/advisories/ra-2025-11-20/
- https://bugzilla.redhat.com/show_bug.cgi?id=2415863
- https://github.com/rnpgp/rnp/commit/7bd9a8dc356aae756b40755be76d36205b6b161a
- https://github.com/rnpgp/rnp
