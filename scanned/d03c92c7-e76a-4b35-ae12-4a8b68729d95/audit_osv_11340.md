# [C] CVE-2017-7471

## Summary
Severity: Critical
Advisory: CVE-2017-7471
CVSS: 9.0 (CVSS:3.1/AV:A/AC:L/PR:L/UI:N/S:C/C:H/I:H/A:H)
Published: 2018-07-09
Source: https://osv.dev/vulnerability/CVE-2017-7471
Type: osv

## Details
Quick Emulator (Qemu) built with the VirtFS, host directory sharing via Plan 9 File System (9pfs) support, is vulnerable to an improper access control issue. It could occur while accessing files on a shared host directory. A privileged user inside guest could use this flaw to access host file system beyond the shared folder and potentially escalating their privileges on a host.

## References
- https://git.qemu.org/?p=qemu.git%3Ba=commitdiff%3Bh=9c6b899f7a46893ab3b671e341a2234e9c0c060e
- http://www.securityfocus.com/bid/97970
- https://security.gentoo.org/glsa/201706-03
- http://www.openwall.com/lists/oss-security/2017/04/19/2
- https://bugzilla.redhat.com/show_bug.cgi?id=CVE-2017-7471
