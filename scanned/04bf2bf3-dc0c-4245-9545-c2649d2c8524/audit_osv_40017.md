# [M] Qemu-kvm: heap buffer overflow in virtio-blk scsi request handling

## Summary
Severity: Medium
Advisory: CVE-2026-48914
CVSS: 6.7 (CVSS:3.1/AV:L/AC:L/PR:H/UI:N/S:C/C:N/I:L/A:H)
Published: 2026-06-12
Source: https://osv.dev/vulnerability/CVE-2026-48914
Type: osv

## Details
A flaw was found in QEMU's virtio-blk device. The issue arises because the device does not properly validate the size of input descriptors before writing data. A malicious guest with high privileges could exploit this vulnerability by submitting a malformed virtio-blk SCSI request, leading to an out-of-bounds write in the host heap memory and a potential denial of service (DoS) for the QEMU process.

## References
- https://access.redhat.com/downloads/content/package-browser/
- https://lore.kernel.org/qemu-devel/20260526154957.1741622-1-stefanha@redhat.com/
- https://access.redhat.com/errata/RHSA-2026:39311
- https://access.redhat.com/errata/RHSA-2026:58571
- https://access.redhat.com/security/cve/CVE-2026-48914
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/48xxx/CVE-2026-48914.json
- https://nvd.nist.gov/vuln/detail/CVE-2026-48914
- https://bugzilla.redhat.com/show_bug.cgi?id=2488283
- https://gitlab.com/qemu-project/qemu
