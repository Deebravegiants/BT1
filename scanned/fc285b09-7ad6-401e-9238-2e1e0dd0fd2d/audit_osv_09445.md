# [M] CVE-2016-9907

## Summary
Severity: Medium
Advisory: CVE-2016-9907
CVSS: 6.5 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:C/C:N/I:N/A:H)
Published: 2016-12-23
Source: https://osv.dev/vulnerability/CVE-2016-9907
Type: osv

## Details
Quick Emulator (Qemu) built with the USB redirector usb-guest support is vulnerable to a memory leakage flaw. It could occur while destroying the USB redirector in 'usbredir_handle_destroy'. A guest user/process could use this issue to leak host memory, resulting in DoS for a host.

## References
- http://www.securityfocus.com/bid/94759
- https://access.redhat.com/errata/RHSA-2017:2392
- https://access.redhat.com/errata/RHSA-2017:2408
- https://lists.debian.org/debian-lts-announce/2018/09/msg00007.html
- https://security.gentoo.org/glsa/201701-49
- http://www.openwall.com/lists/oss-security/2016/12/08/3
