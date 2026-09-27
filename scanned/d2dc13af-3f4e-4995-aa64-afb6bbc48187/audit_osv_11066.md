# [H] CVE-2017-5931

## Summary
Severity: High
Advisory: CVE-2017-5931
CVSS: 8.8 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:C/C:H/I:H/A:H)
Published: 2017-03-27
Source: https://osv.dev/vulnerability/CVE-2017-5931
Type: osv

## Details
Integer overflow in hw/virtio/virtio-crypto.c in QEMU (aka Quick Emulator) allows local guest OS privileged users to cause a denial of service (QEMU process crash) or possibly execute arbitrary code on the host via a crafted virtio-crypto request, which triggers a heap-based buffer overflow.

## References
- http://git.qemu-project.org/?p=qemu.git%3Ba=commit%3Bh=a08aaff811fb194950f79711d2afe5a892ae03a4
- http://www.securityfocus.com/bid/96141
- https://security.gentoo.org/glsa/201702-28
- http://www.openwall.com/lists/oss-security/2017/02/08/2
- https://bugzilla.redhat.com/show_bug.cgi?id=1420092
- https://lists.nongnu.org/archive/html/qemu-devel/2017-01/msg01368.html
