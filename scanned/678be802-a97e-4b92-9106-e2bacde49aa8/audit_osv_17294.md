# [M] CVE-2020-14364

## Summary
Severity: Medium
Advisory: CVE-2020-14364
CVSS: 5.0 (CVSS:3.1/AV:L/AC:H/PR:H/UI:N/S:C/C:L/I:L/A:L)
Published: 2020-08-31
Source: https://osv.dev/vulnerability/CVE-2020-14364
Type: osv

## Details
An out-of-bounds read/write access flaw was found in the USB emulator of the QEMU in versions before 5.2.0. This issue occurs while processing USB packets from a guest when USBDevice 'setup_len' exceeds its 'data_buf[4096]' in the do_token_in, do_token_out routines. This flaw allows a guest user to crash the QEMU process, resulting in a denial of service, or the potential execution of arbitrary code with the privileges of the QEMU process on the host.

## References
- https://lists.fedoraproject.org/archives/list/package-announce%40lists.fedoraproject.org/message/JTZQUQ6ZBPMFMNAUQBVJFELYNMUZLL6P/
- https://lists.fedoraproject.org/archives/list/package-announce%40lists.fedoraproject.org/message/M52WIRMZL6TZRYZ65N6OAYNNFHV62O2N/
- http://lists.opensuse.org/opensuse-security-announce/2020-10/msg00024.html
- https://lists.debian.org/debian-lts-announce/2020/09/msg00013.html
- https://security.gentoo.org/glsa/202009-14
- https://security.gentoo.org/glsa/202011-09
- https://security.netapp.com/advisory/ntap-20200924-0006/
- https://usn.ubuntu.com/4511-1/
- https://www.debian.org/security/2020/dsa-4760
- https://www.openwall.com/lists/oss-security/2020/08/24/2
- https://www.openwall.com/lists/oss-security/2020/08/24/3
- https://bugzilla.redhat.com/show_bug.cgi?id=1869201
