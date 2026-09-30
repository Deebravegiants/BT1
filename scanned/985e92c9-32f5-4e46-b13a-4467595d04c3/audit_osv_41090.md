# [C] Out-of-bounds Write in Firecracker virtio-pci Transport

## Summary
Severity: Critical
Advisory: CVE-2026-5747
Aliases: GHSA-776c-mpj7-jm3r
CVSS: 9.0 (CVSS:4.0/AV:L/AC:H/AT:P/PR:H/UI:N/VC:H/VI:H/VA:H/SC:H/SI:H/SA:H)
Published: 2026-04-07
Source: https://osv.dev/vulnerability/CVE-2026-5747
Type: osv

## Details
An out-of-bounds write issue in the virtio PCI transport in Firecracker 1.13.0 through 1.14.3 and 1.15.0 on x86_64 and aarch64 might allow a local guest user with root privileges to crash the Firecracker VMM process or potentially execute arbitrary code on the host via modification of virtio queue configuration registers after device activation. Achieving code execution on the host requires additional preconditions, such as the use of a custom guest kernel or specific snapshot configurations.

To remediate this, users should upgrade to Firecracker 1.14.4 or 1.15.1 and later.

## References
- https://aws.amazon.com/security/security-bulletins/2026-015-aws/
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/5xxx/CVE-2026-5747.json
- https://github.com/firecracker-microvm/firecracker/security/advisories/GHSA-776c-mpj7-jm3r
- https://nvd.nist.gov/vuln/detail/CVE-2026-5747
- https://github.com/firecracker-microvm/firecracker/releases/tag/v1.14.4
- https://github.com/firecracker-microvm/firecracker/releases/tag/v1.15.1
