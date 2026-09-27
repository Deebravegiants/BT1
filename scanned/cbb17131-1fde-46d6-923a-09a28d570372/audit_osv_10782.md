# [C] CVE-2017-2620

## Summary
Severity: Critical
Advisory: CVE-2017-2620
CVSS: 9.9 (CVSS:3.0/AV:N/AC:L/PR:L/UI:N/S:C/C:H/I:H/A:H)
Published: 2018-07-27
Source: https://osv.dev/vulnerability/CVE-2017-2620
Type: osv

## Details
Quick emulator (QEMU) before 2.8 built with the Cirrus CLGD 54xx VGA Emulator support is vulnerable to an out-of-bounds access issue. The issue could occur while copying VGA data in cirrus_bitblt_cputovideo. A privileged user inside guest could use this flaw to crash the QEMU process OR potentially execute arbitrary code on host with privileges of the QEMU process.

## References
- https://lists.debian.org/debian-lts-announce/2018/09/msg00007.html
- http://rhn.redhat.com/errata/RHSA-2017-0328.html
- http://rhn.redhat.com/errata/RHSA-2017-0329.html
- http://rhn.redhat.com/errata/RHSA-2017-0330.html
- http://rhn.redhat.com/errata/RHSA-2017-0331.html
- http://rhn.redhat.com/errata/RHSA-2017-0332.html
- http://rhn.redhat.com/errata/RHSA-2017-0333.html
- http://rhn.redhat.com/errata/RHSA-2017-0334.html
- http://rhn.redhat.com/errata/RHSA-2017-0350.html
- http://rhn.redhat.com/errata/RHSA-2017-0351.html
- http://rhn.redhat.com/errata/RHSA-2017-0352.html
- http://rhn.redhat.com/errata/RHSA-2017-0396.html
- http://rhn.redhat.com/errata/RHSA-2017-0454.html
- http://www.openwall.com/lists/oss-security/2017/02/21/1
- http://www.securityfocus.com/bid/96378
- http://www.securitytracker.com/id/1037870
- https://lists.debian.org/debian-lts-announce/2018/02/msg00005.html
- https://security.gentoo.org/glsa/201703-07
- https://security.gentoo.org/glsa/201704-01
- https://support.citrix.com/article/CTX220771
