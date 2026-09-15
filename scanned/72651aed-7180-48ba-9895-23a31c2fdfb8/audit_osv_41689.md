# [C] Arbitrary File Read/Write: metadata.yaml symlink in image allows host filesystem access as root

## Summary
Severity: Critical
Advisory: CVE-2026-63293
Aliases: GHSA-j825-cg34-5fr5
CVSS: 9.9 (CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:C/C:H/I:H/A:H)
Published: 2026-08-12
Source: https://osv.dev/vulnerability/CVE-2026-63293
Type: osv

## Details
A link following vulnerability in LXD allows an attacker to achieve arbitrary file read and write operations on the host system. When importing or unpacking an image archive, LXD fails to validate whether the metadata.yaml file is a symbolic link. An attacker can exploit this flaw by providing a crafted image archive with a symlinked metadata.yaml file pointing to target file paths on the host system.

## References
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/63xxx/CVE-2026-63293.json
- https://github.com/canonical/lxd/security/advisories/GHSA-j825-cg34-5fr5
- https://nvd.nist.gov/vuln/detail/CVE-2026-63293
- https://github.com/canonical/lxd
