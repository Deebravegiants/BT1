# [H] CVE-2017-7487

## Summary
Severity: High
Advisory: CVE-2017-7487
CVSS: 7.8 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H)
Published: 2017-05-14
Source: https://osv.dev/vulnerability/CVE-2017-7487
Type: osv

## Details
The ipxitf_ioctl function in net/ipx/af_ipx.c in the Linux kernel through 4.11.1 mishandles reference counts, which allows local users to cause a denial of service (use-after-free) or possibly have unspecified other impact via a failed SIOCGIFADDR ioctl call for an IPX interface.

## References
- https://source.android.com/security/bulletin/2017-09-01
- http://www.debian.org/security/2017/dsa-3886
- http://www.securityfocus.com/bid/98439
- http://www.securitytracker.com/id/1039237
- http://git.kernel.org/cgit/linux/kernel/git/torvalds/linux.git/commit/?id=ee0d8d8482345ff97a75a7d747efc309f13b0d80
- https://bugzilla.redhat.com/show_bug.cgi?id=1447734
- https://github.com/torvalds/linux/commit/ee0d8d8482345ff97a75a7d747efc309f13b0d80
- https://patchwork.ozlabs.org/patch/757549/
