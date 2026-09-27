# [H] `calamares-nixos-extensions` LUKS keyfile exposure

## Summary
Severity: High
Advisory: CVE-2023-36476
Aliases: GHSA-3rvf-24q2-24ww
CVSS: 7.9 (CVSS:3.1/AV:L/AC:L/PR:N/UI:N/S:C/C:H/I:L/A:N)
Published: 2023-06-29
Source: https://osv.dev/vulnerability/CVE-2023-36476
Type: osv

## Details
calamares-nixos-extensions provides Calamares branding and modules for NixOS, a distribution of GNU/Linux. Users of calamares-nixos-extensions version 0.3.12 and prior who installed NixOS through the graphical calamares installer, with an unencrypted `/boot`, on either non-UEFI systems or with a LUKS partition different from `/` have their LUKS key file in `/boot` as a plaintext CPIO archive attached to their NixOS initrd. A patch is available and anticipated to be part of version 0.3.13 to backport to NixOS 22.11, 23.05, and unstable channels. Expert users who have a copy of their data may, as a workaround, re-encrypt the LUKS partition(s) themselves.

## References
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2023/36xxx/CVE-2023-36476.json
- https://github.com/NixOS/calamares-nixos-extensions/security/advisories/GHSA-3rvf-24q2-24ww
- https://nvd.nist.gov/vuln/detail/CVE-2023-36476
- https://github.com/osresearch/heads/issues/1348
- https://github.com/vlinkz/calamares-nixos-extensions/commit/837ca4da5521a74d3b5ca6f7b88890a6713faa22
