# [M] EVE Doesn't Protect Rootfs

## Summary
Severity: Medium
Advisory: GHSA-5h7v-g49c-h887
CVE: CVE-2023-43636
CWE: CWE-345
Ecosystem: Go
CVSS: CVSS:3.1/AV:P/AC:H/PR:L/UI:N/S:C/C:H/I:H/A:N (CVSS_V3)
Published: 2026-02-04
Source: https://github.com/advisories/GHSA-5h7v-g49c-h887
Type: github-advisory

## Affected
- Go: `github.com/lf-edge/eve/pkg/grub` — affected >=0 <0.0.0-20220708121648-5fef4d92e758

## Details
### Impact

Measured boot validates BIOS, grub, kernel cmdline, and initrd but not the entire rootfs. Thus, an attacker can create an EVE-OS rootfs squashfs image with some files modified and take out the disk and replace the existing rootfs image without that being detected by measure boot and remote attestation.

### Patches

Fixed in 8.6.0 and 8.12.1-lts

### Workarounds

None

## References
- https://github.com/lf-edge/eve/security/advisories/GHSA-5h7v-g49c-h887
- https://nvd.nist.gov/vuln/detail/CVE-2023-43636
- https://github.com/lf-edge/eve/commit/5fef4d92e75838cc78010edaed5247dfbdae1889
- https://github.com/lf-edge/eve/commit/aa3501d6c57206ced222c33aea15a9169d629141
- https://asrg.io/security-advisories/19274
- https://asrg.io/security-advisories/cve-2023-43636
- https://github.com/lf-edge/eve
