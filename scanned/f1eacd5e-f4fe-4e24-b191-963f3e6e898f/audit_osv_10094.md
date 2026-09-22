# [M] CVE-2017-13673

## Summary
Severity: Medium
Advisory: CVE-2017-13673
CVSS: 6.5 (CVSS:3.0/AV:N/AC:L/PR:L/UI:N/S:U/C:N/I:N/A:H)
Published: 2017-08-29
Source: https://osv.dev/vulnerability/CVE-2017-13673
Type: osv

## Details
The vga display update in mis-calculated the region for the dirty bitmap snapshot in case split screen mode is used causing a denial of service (assertion failure) in the cpu_physical_memory_snapshot_get_dirty function.

## References
- http://lists.opensuse.org/opensuse-security-announce/2019-03/msg00042.html
- http://www.openwall.com/lists/oss-security/2017/09/10/1
- https://git.qemu.org/gitweb.cgi?p=qemu.git%3Ba=commit%3Bh=bfc56535f793c557aa754c50213fc5f882e6482d
- http://www.securityfocus.com/bid/100527
- https://access.redhat.com/errata/RHSA-2018:1104
- https://access.redhat.com/errata/RHSA-2018:1113
- https://lists.gnu.org/archive/html/qemu-devel/2017-08/msg04685.html
