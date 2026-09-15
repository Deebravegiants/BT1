# [H] CVE-2016-1568

## Summary
Severity: High
Advisory: CVE-2016-1568
CVSS: 8.8 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:C/C:H/I:H/A:H)
Published: 2016-04-12
Source: https://osv.dev/vulnerability/CVE-2016-1568
Type: osv

## Details
Use-after-free vulnerability in hw/ide/ahci.c in QEMU, when built with IDE AHCI Emulation support, allows guest OS users to cause a denial of service (instance crash) or possibly execute arbitrary code via an invalid AHCI Native Command Queuing (NCQ) AIO command.

## References
- http://git.qemu.org/?p=qemu.git%3Ba=commit%3Bh=4ab0359a8ae182a7ac5c99609667273167703fab
- http://rhn.redhat.com/errata/RHSA-2016-0084.html
- http://rhn.redhat.com/errata/RHSA-2016-0086.html
- http://rhn.redhat.com/errata/RHSA-2016-0087.html
- http://rhn.redhat.com/errata/RHSA-2016-0088.html
- http://www.debian.org/security/2016/dsa-3469
- http://www.debian.org/security/2016/dsa-3470
- http://www.debian.org/security/2016/dsa-3471
- http://www.openwall.com/lists/oss-security/2016/01/09/1
- http://www.openwall.com/lists/oss-security/2016/01/09/2
- http://www.securityfocus.com/bid/80191
- http://www.securitytracker.com/id/1034859
- https://security.gentoo.org/glsa/201602-01
