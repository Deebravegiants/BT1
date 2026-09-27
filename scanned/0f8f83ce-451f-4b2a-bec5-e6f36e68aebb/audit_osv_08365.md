# [H] CVE-2016-2538

## Summary
Severity: High
Advisory: CVE-2016-2538
CVSS: 7.1 (CVSS:3.0/AV:L/AC:L/PR:L/UI:N/S:U/C:H/I:N/A:H)
Published: 2016-06-16
Source: https://osv.dev/vulnerability/CVE-2016-2538
Type: osv

## Details
Multiple integer overflows in the USB Net device emulator (hw/usb/dev-network.c) in QEMU before 2.5.1 allow local guest OS administrators to cause a denial of service (QEMU process crash) or obtain sensitive host memory information via a remote NDIS control message packet that is mishandled in the (1) rndis_query_response, (2) rndis_set_response, or (3) usb_net_handle_dataout function.

## References
- http://git.qemu.org/?p=qemu.git%3Ba=commit%3Bh=fe3c546c5ff2a6210f9a4d8561cc64051ca8603e
- http://lists.nongnu.org/archive/html/qemu-stable/2016-03/msg00064.html
- http://www.openwall.com/lists/oss-security/2016/02/22/3
- http://www.securityfocus.com/bid/83336
- https://lists.debian.org/debian-lts-announce/2018/11/msg00038.html
- https://lists.gnu.org/archive/html/qemu-devel/2016-02/msg03658.html
- http://www.ubuntu.com/usn/USN-2974-1
- https://security.gentoo.org/glsa/201604-01
- https://bugzilla.redhat.com/show_bug.cgi?id=1303120
