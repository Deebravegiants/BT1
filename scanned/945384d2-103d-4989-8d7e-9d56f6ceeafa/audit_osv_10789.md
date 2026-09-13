# [M] CVE-2017-2633

## Summary
Severity: Medium
Advisory: CVE-2017-2633
CVSS: 6.5 (CVSS:3.0/AV:N/AC:L/PR:L/UI:N/S:U/C:N/I:N/A:H)
Published: 2018-07-27
Source: https://osv.dev/vulnerability/CVE-2017-2633
Type: osv

## Details
An out-of-bounds memory access issue was found in Quick Emulator (QEMU) before 1.7.2 in the VNC display driver. This flaw could occur while refreshing the VNC display surface area in the 'vnc_refresh_server_surface'. A user inside a guest could use this flaw to crash the QEMU process.

## References
- https://git.qemu.org/?p=qemu.git%3Ba=commitdiff%3Bh=9f64916da20eea67121d544698676295bbb105a7
- https://git.qemu.org/?p=qemu.git%3Ba=commitdiff%3Bh=bea60dd7679364493a0d7f5b54316c767cf894ef
- http://www.securityfocus.com/bid/96417
- https://access.redhat.com/errata/RHSA-2017:1205
- https://access.redhat.com/errata/RHSA-2017:1206
- https://access.redhat.com/errata/RHSA-2017:1441
- https://access.redhat.com/errata/RHSA-2017:1856
- http://www.openwall.com/lists/oss-security/2017/02/23/1
- https://bugzilla.redhat.com/show_bug.cgi?id=CVE-2017-2633
