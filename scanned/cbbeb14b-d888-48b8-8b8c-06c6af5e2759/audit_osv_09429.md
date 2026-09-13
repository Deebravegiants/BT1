# [M] CVE-2016-9846

## Summary
Severity: Medium
Advisory: CVE-2016-9846
CVSS: 6.5 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:C/C:N/I:N/A:H)
Published: 2016-12-29
Source: https://osv.dev/vulnerability/CVE-2016-9846
Type: osv

## Details
QEMU (aka Quick Emulator) built with the Virtio GPU Device emulator support is vulnerable to a memory leakage issue. It could occur while updating the cursor data in update_cursor_data_virgl. A guest user/process could use this flaw to leak host memory bytes, resulting in DoS for a host.

## References
- http://www.openwall.com/lists/oss-security/2016/12/05/18
- http://www.openwall.com/lists/oss-security/2016/12/05/23
- http://www.securityfocus.com/bid/94765
- https://security.gentoo.org/glsa/201701-49
- https://lists.gnu.org/archive/html/qemu-devel/2016-11/msg00029.html
