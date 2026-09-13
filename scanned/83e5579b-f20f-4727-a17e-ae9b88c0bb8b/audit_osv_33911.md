# [H] NeKernal Multiple Memory Corruption Vulnerabilities in mkfs.hefs

## Summary
Severity: High
Advisory: CVE-2025-52568
Aliases: GHSA-cmp2-5f6g-mw34
CVSS: 7.5 (CVSS:4.0/AV:N/AC:L/AT:N/PR:N/UI:N/VC:N/VI:H/VA:H/SC:N/SI:N/SA:N)
Published: 2025-06-24
Source: https://osv.dev/vulnerability/CVE-2025-52568
Type: osv

## Details
NeKernal is a free and open-source operating system stack. Prior to version 0.0.3, there are several memory safety issues that can lead to memory corruption, disk image corruption, denial of service, and potential code execution. These issues stem from unchecked memory operations, unsafe typecasting, and improper input validation. This issue has been patched in version 0.0.3.

## References
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2025/52xxx/CVE-2025-52568.json
- https://github.com/nekernel-org/nekernel/security/advisories/GHSA-cmp2-5f6g-mw34
- https://nvd.nist.gov/vuln/detail/CVE-2025-52568
- https://github.com/nekernel-org/nekernel/commit/6506875ad0ab210b82a5c4ce227bf851508de17d
- https://github.com/nekernel-org/nekernel/commit/6511afbf405c31513bc88ab06bca58218610a994
- https://github.com/nekernel-org/nekernel/pull/35
- https://github.com/nekernel-org/nekernel/pull/36
