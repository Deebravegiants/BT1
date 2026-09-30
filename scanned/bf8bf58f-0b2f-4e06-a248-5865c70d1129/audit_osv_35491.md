# [M] Qemu-kvm: heap off-by-one in kvm xen physdevop_map_pirq

## Summary
Severity: Medium
Advisory: CVE-2026-0665
CVSS: 6.5 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:C/C:N/I:N/A:H)
Published: 2026-02-18
Source: https://osv.dev/vulnerability/CVE-2026-0665
Type: osv

## Details
An off-by-one error was found in QEMU's KVM Xen guest support. A malicious guest could use this flaw to trigger out-of-bounds heap accesses in the QEMU process via the emulated Xen physdev hypercall interface, leading to a denial of service or potential memory corruption.

## References
- https://access.redhat.com/downloads/content/package-browser/
- https://access.redhat.com/security/cve/CVE-2026-0665
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/0xxx/CVE-2026-0665.json
- https://nvd.nist.gov/vuln/detail/CVE-2026-0665
- https://bugzilla.redhat.com/show_bug.cgi?id=2428640
- https://gitlab.com/qemu-project/qemu
