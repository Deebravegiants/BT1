# [M] CVE-2016-9921

## Summary
Severity: Medium
Advisory: CVE-2016-9921
CVSS: 6.5 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:C/C:N/I:N/A:H)
Published: 2016-12-23
Source: https://osv.dev/vulnerability/CVE-2016-9921
Type: osv

## Details
Quick emulator (Qemu) built with the Cirrus CLGD 54xx VGA Emulator support is vulnerable to a divide by zero issue. It could occur while copying VGA data when cirrus graphics mode was set to be VGA. A privileged user inside guest could use this flaw to crash the Qemu process instance on the host, resulting in DoS.

## References
- http://www.securityfocus.com/bid/94803
- https://access.redhat.com/errata/RHSA-2017:2392
- https://access.redhat.com/errata/RHSA-2017:2408
- https://lists.debian.org/debian-lts-announce/2018/09/msg00007.html
- https://security.gentoo.org/glsa/201701-49
- http://www.openwall.com/lists/oss-security/2016/12/09/1
