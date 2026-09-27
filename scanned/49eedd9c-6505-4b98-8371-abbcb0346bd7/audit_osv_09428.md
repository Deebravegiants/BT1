# [M] CVE-2016-9845

## Summary
Severity: Medium
Advisory: CVE-2016-9845
CVSS: 6.5 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:C/C:H/I:N/A:N)
Published: 2016-12-29
Source: https://osv.dev/vulnerability/CVE-2016-9845
Type: osv

## Details
QEMU (aka Quick Emulator) built with the Virtio GPU Device emulator support is vulnerable to an information leakage issue. It could occur while processing 'VIRTIO_GPU_CMD_GET_CAPSET_INFO' command. A guest user/process could use this flaw to leak contents of the host memory bytes.

## References
- http://www.openwall.com/lists/oss-security/2016/12/05/15
- http://www.openwall.com/lists/oss-security/2016/12/05/22
- http://www.securityfocus.com/bid/94763
- https://security.gentoo.org/glsa/201701-49
- https://lists.nongnu.org/archive/html/qemu-devel/2016-11/msg00019.html
