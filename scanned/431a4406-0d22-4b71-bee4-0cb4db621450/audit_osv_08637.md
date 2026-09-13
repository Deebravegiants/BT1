# [M] CVE-2016-5011

## Summary
Severity: Medium
Advisory: CVE-2016-5011
CVSS: 4.6 (CVSS:3.1/AV:P/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:H)
Published: 2017-04-11
Source: https://osv.dev/vulnerability/CVE-2016-5011
Type: osv

## Details
The parse_dos_extended function in partitions/dos.c in the libblkid library in util-linux allows physically proximate attackers to cause a denial of service (memory consumption) via a crafted MSDOS partition table with an extended partition boot record at zero offset.

## References
- http://rhn.redhat.com/errata/RHSA-2016-2605.html
- http://www-01.ibm.com/support/docview.wss?uid=isg3T1024543
- http://www-01.ibm.com/support/docview.wss?uid=nas8N1021801
- http://www.securityfocus.com/bid/91683
- http://www.securitytracker.com/id/1036272
- http://www.openwall.com/lists/oss-security/2016/07/11/2
- https://git.kernel.org/pub/scm/utils/util-linux/util-linux.git/commit/?id=7164a1c3
