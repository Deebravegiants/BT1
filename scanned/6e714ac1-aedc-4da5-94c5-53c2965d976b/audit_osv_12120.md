# [M] CVE-2018-10373

## Summary
Severity: Medium
Advisory: CVE-2018-10373
CVSS: 6.5 (CVSS:3.0/AV:N/AC:L/PR:N/UI:R/S:U/C:N/I:N/A:H)
Published: 2018-04-25
Source: https://osv.dev/vulnerability/CVE-2018-10373
Type: osv

## Details
concat_filename in dwarf2.c in the Binary File Descriptor (BFD) library (aka libbfd), as distributed in GNU Binutils 2.30, allows remote attackers to cause a denial of service (NULL pointer dereference and application crash) via a crafted binary file, as demonstrated by nm-new.

## References
- https://usn.ubuntu.com/4336-1/
- http://www.securityfocus.com/bid/104000
- https://access.redhat.com/errata/RHBA-2019:0327
- https://access.redhat.com/errata/RHSA-2018:3032
- https://security.gentoo.org/glsa/201908-01
- https://sourceware.org/bugzilla/show_bug.cgi?id=23065
