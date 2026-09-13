# [H] rsync < 3.5.0 Path Confinement Bypass via /./ Boundary Marker in Chroot Mode

## Summary
Severity: High
Advisory: CVE-2026-53793
Aliases: GHSA-wj7w-vh23-mm44
CVSS: 7.5 (CVSS:4.0/AV:N/AC:H/AT:P/PR:N/UI:N/VC:H/VI:H/VA:N/SC:N/SI:N/SA:N)
Published: 2026-08-13
Source: https://osv.dev/vulnerability/CVE-2026-53793
Type: osv

## Details
rsync before 3.5.0 contains a path confinement bypass vulnerability that allows remote clients to escape the intended inner-module root confinement by constructing paths that resolve outside the chroot boundary when the module root contains a /./ boundary marker. Attackers can exploit improper handling of the /./ notation or forge delta-basis transfers referencing xname paths that cross the /./ boundary to gain unauthorized read or write access to files outside the module's subtree.

## References
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/53xxx/CVE-2026-53793.json
- https://github.com/RsyncProject/rsync/releases/tag/v3.5.0
- https://github.com/RsyncProject/rsync/security/advisories/GHSA-wj7w-vh23-mm44
- https://nvd.nist.gov/vuln/detail/CVE-2026-53793
- https://www.vulncheck.com/advisories/rsync-path-confinement-bypass-via-boundary-marker-in-chroot-mode
- https://github.com/RsyncProject/rsync
