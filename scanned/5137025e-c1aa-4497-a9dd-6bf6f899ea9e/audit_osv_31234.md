# [M] Qemu-kvm: virtio-net: queue index out-of-bounds access in software rss

## Summary
Severity: Medium
Advisory: CVE-2024-6505
CVSS: 6.8 (CVSS:3.1/AV:N/AC:L/PR:H/UI:N/S:C/C:N/I:N/A:H)
Published: 2024-07-05
Source: https://osv.dev/vulnerability/CVE-2024-6505
Type: osv

## Details
A flaw was found in the virtio-net device in QEMU. When enabling the RSS feature on the virtio-net network card, the indirections_table data within RSS becomes controllable. Setting excessively large values may cause an index out-of-bounds issue, potentially resulting in heap overflow access. This flaw allows a privileged user in the guest to crash the QEMU process on the host.

## References
- https://access.redhat.com/downloads/content/package-browser/
- https://access.redhat.com/security/cve/CVE-2024-6505
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2024/6xxx/CVE-2024-6505.json
- https://nvd.nist.gov/vuln/detail/CVE-2024-6505
- https://security.netapp.com/advisory/ntap-20240816-0006/
- https://bugzilla.redhat.com/show_bug.cgi?id=2295760
- https://gitlab.com/qemu-project/qemu
