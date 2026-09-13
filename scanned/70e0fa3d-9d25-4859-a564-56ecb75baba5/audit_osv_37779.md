# [H] barebox: FIT Signature Verification Bypass Vulnerability

## Summary
Severity: High
Advisory: CVE-2026-33243
Aliases: CVE-2026-46728, GHSA-3fvj-q26p-j6h4
CVSS: 8.2 (CVSS:3.1/AV:L/AC:L/PR:H/UI:N/S:C/C:H/I:H/A:H)
Published: 2026-03-20
Source: https://osv.dev/vulnerability/CVE-2026-33243
Type: osv

## Details
barebox is a bootloader. In barebox from version 2016.03.0 to before version 2026.03.1 (and the corresponding backport to 2025.09.3), an attacker could exploit a FIT signature verification vulnerability to trick the bootloader into booting different images than those that were verified as part of a signed configuration. mkimage(1) sets the hashed-nodes property of the FIT signature node to list which nodes of the FIT were hashed as part of the signing process as these will need to be verified later on by the bootloader. However, hashed-nodes itself is not part of the hash and could therefore be modified to allow booting different images than those that have been verified. This issue has been patched in barebox versions 2026.03.1 and backported to 2025.09.3.

## References
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/33xxx/CVE-2026-33243.json
- https://github.com/barebox/barebox/security/advisories/GHSA-3fvj-q26p-j6h4
- https://nvd.nist.gov/vuln/detail/CVE-2026-33243
- https://github.com/barebox/barebox/commit/aca01795056d51060cb096f9a1ea309361743e05
