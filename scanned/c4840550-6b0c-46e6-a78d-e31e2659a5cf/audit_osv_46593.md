# [M] CVE-2014-0148

## Summary
Severity: Medium
Advisory: CVE-2014-0148
CVSS: 5.5 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:N/I:N/A:H)
Published: 2022-09-29
Source: https://osv.dev/vulnerability/CVE-2014-0148
Type: osv

## Details
Qemu before 2.0 block driver for Hyper-V VHDX Images is vulnerable to infinite loops and other potential issues when calculating BAT entries, due to missing bounds checks for block_size and logical_sector_size variables. These are used to derive other fields like 'sectors_per_block' etc. A user able to alter the Qemu disk image could ise this flaw to crash the Qemu instance resulting in DoS.

## References
- http://rhn.redhat.com/errata/RHSA-2014-0420.html
- http://rhn.redhat.com/errata/RHSA-2014-0421.html
- http://www.openwall.com/lists/oss-security/2014/03/26/8
- https://bugzilla.redhat.com/show_bug.cgi?id=1078212
- https://lists.gnu.org/archive/html/qemu-devel/2014-03/msg04994.html
- http://www.openwall.com/lists/oss-security/2014/03/26/8
- https://lists.gnu.org/archive/html/qemu-devel/2014-03/msg04994.html
- http://www.openwall.com/lists/oss-security/2014/03/26/8
- https://bugzilla.redhat.com/show_bug.cgi?id=1078212
- https://lists.gnu.org/archive/html/qemu-devel/2014-03/msg04994.html
- https://bugzilla.redhat.com/show_bug.cgi?id=1078212
- http://git.qemu.org/?p=qemu.git%3Ba=commit%3Bh=1d7678dec4761acdc43439da6ceda41a703ba1a6
