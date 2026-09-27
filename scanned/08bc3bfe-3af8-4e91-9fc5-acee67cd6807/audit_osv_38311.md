# [H] Qemu-kvm: hyperv/syndbg: missing mapped-length guard after cpu_physical_memory_map causes host oob write

## Summary
Severity: High
Advisory: CVE-2026-3842
CVSS: 7.8 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H)
Published: 2026-07-16
Source: https://osv.dev/vulnerability/CVE-2026-3842
Type: osv

## Details
A flaw was found in QEMU. This vulnerability allows a local attacker within a guest virtual machine to write data beyond its allocated memory. This occurs when cpu_physical_memory_map() returns a shorter length than expected, leading to an out-of-bounds write. Successful exploitation could result in unauthorized access to guest memory or corruption of heap-allocated objects, potentially causing information disclosure, data integrity issues, or a denial of service.

## References
- https://access.redhat.com/downloads/content/package-browser/
- https://security.access.redhat.com/data/csaf/v2/vex/2026/cve-2026-3842.json
- https://access.redhat.com/security/cve/CVE-2026-3842
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/3xxx/CVE-2026-3842.json
- https://nvd.nist.gov/vuln/detail/CVE-2026-3842
- https://bugzilla.redhat.com/show_bug.cgi?id=2458150
- https://gitlab.com/qemu-project/qemu
