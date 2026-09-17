# [M] Qemu: virtio-net: stack buffer overflow in virtio_net_flush_tx()

## Summary
Severity: Medium
Advisory: CVE-2023-6693
CVSS: 4.9 (CVSS:3.1/AV:L/AC:H/PR:N/UI:N/S:U/C:L/I:L/A:L)
Published: 2024-01-02
Source: https://osv.dev/vulnerability/CVE-2023-6693
Type: osv

## Details
A stack based buffer overflow was found in the virtio-net device of QEMU. This issue occurs when flushing TX in the virtio_net_flush_tx function if guest features VIRTIO_NET_F_HASH_REPORT, VIRTIO_F_VERSION_1 and VIRTIO_NET_F_MRG_RXBUF are enabled. This could allow a malicious user to overwrite local variables allocated on the stack. Specifically, the `out_sg` variable could be used to read a part of process memory and send it to the wire, causing an information leak.

## References
- https://access.redhat.com/downloads/content/package-browser/
- https://lists.debian.org/debian-lts-announce/2025/04/msg00042.html
- https://lists.fedoraproject.org/archives/list/package-announce@lists.fedoraproject.org/message/OYGUN5HVOXESW7MSNM44E4AE2VNXQB6Y/
- https://access.redhat.com/errata/RHSA-2024:2962
- https://access.redhat.com/errata/RHSA-2025:4492
- https://access.redhat.com/security/cve/CVE-2023-6693
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2023/6xxx/CVE-2023-6693.json
- https://nvd.nist.gov/vuln/detail/CVE-2023-6693
- https://security.netapp.com/advisory/ntap-20240208-0004/
- https://bugzilla.redhat.com/show_bug.cgi?id=2254580
