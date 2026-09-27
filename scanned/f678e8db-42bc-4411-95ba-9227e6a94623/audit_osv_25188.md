# [M] Heap buffer overflow in virtio_crypto_sym_op_helper()

## Summary
Severity: Medium
Advisory: CVE-2023-3180
CVSS: 6.0 (CVSS:3.1/AV:L/AC:L/PR:H/UI:N/S:C/C:N/I:N/A:H)
Published: 2023-08-03
Source: https://osv.dev/vulnerability/CVE-2023-3180
Type: osv

## Details
A flaw was found in the QEMU virtual crypto device while handling data encryption/decryption requests in virtio_crypto_handle_sym_req. There is no check for the value of `src_len` and `dst_len` in virtio_crypto_sym_op_helper, potentially leading to a heap buffer overflow when the two values differ.

## References
- https://access.redhat.com/downloads/content/package-browser/
- https://lists.debian.org/debian-lts-announce/2023/10/msg00006.html
- https://lists.fedoraproject.org/archives/list/package-announce@lists.fedoraproject.org/message/MURWGXDIF2WTDXV36T6HFJDBL632AO7R/
- https://packages.fedoraproject.org/
- https://access.redhat.com/security/cve/CVE-2023-3180
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2023/3xxx/CVE-2023-3180.json
- https://nvd.nist.gov/vuln/detail/CVE-2023-3180
- https://security.netapp.com/advisory/ntap-20230831-0008/
- https://bugzilla.redhat.com/show_bug.cgi?id=2222424
