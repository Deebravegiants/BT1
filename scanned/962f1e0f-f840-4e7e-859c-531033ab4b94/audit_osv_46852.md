# [M] CVE-2015-5745

## Summary
Severity: Medium
Advisory: CVE-2015-5745
CVSS: 6.5 (CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:N/I:N/A:H)
Published: 2020-01-23
Source: https://osv.dev/vulnerability/CVE-2015-5745
Type: osv

## Details
Buffer overflow in the send_control_msg function in hw/char/virtio-serial-bus.c in QEMU before 2.4.0 allows guest users to cause a denial of service (QEMU process crash) via a crafted virtio control message.

## References
- http://lists.fedoraproject.org/pipermail/package-announce/2015-October/168077.html
- http://lists.fedoraproject.org/pipermail/package-announce/2015-October/168646.html
- http://lists.fedoraproject.org/pipermail/package-announce/2015-October/168671.html
- http://www.openwall.com/lists/oss-security/2015/08/06/3
- http://www.openwall.com/lists/oss-security/2015/08/06/5
- https://github.com/qemu/qemu/commit/7882080388be5088e72c425b02223c02e6cb4295
- https://lists.gnu.org/archive/html/qemu-devel/2015-07/msg05458.html
- https://www.arista.com/en/support/advisories-notices/security-advisories/1180-security-advisory-13
- http://lists.fedoraproject.org/pipermail/package-announce/2015-October/168077.html
- http://lists.fedoraproject.org/pipermail/package-announce/2015-October/168646.html
- http://lists.fedoraproject.org/pipermail/package-announce/2015-October/168671.html
- http://www.openwall.com/lists/oss-security/2015/08/06/3
- http://www.openwall.com/lists/oss-security/2015/08/06/5
- https://lists.gnu.org/archive/html/qemu-devel/2015-07/msg05458.html
- http://www.openwall.com/lists/oss-security/2015/08/06/5
- https://github.com/qemu/qemu/commit/7882080388be5088e72c425b02223c02e6cb4295
- https://lists.gnu.org/archive/html/qemu-devel/2015-07/msg05458.html
