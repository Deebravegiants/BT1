# [M] CVE-2019-3812

## Summary
Severity: Medium
Advisory: CVE-2019-3812
CVSS: 5.5 (CVSS:3.0/AV:L/AC:L/PR:L/UI:N/S:U/C:H/I:N/A:N)
Published: 2019-02-19
Source: https://osv.dev/vulnerability/CVE-2019-3812
Type: osv

## Details
QEMU, through version 2.10 and through version 3.1.0, is vulnerable to an out-of-bounds read of up to 128 bytes in the hw/i2c/i2c-ddc.c:i2c_ddc() function. A local attacker with permission to execute i2c commands could exploit this to read stack memory of the qemu process on the host.

## References
- http://lists.opensuse.org/opensuse-security-announce/2019-05/msg00040.html
- https://lists.fedoraproject.org/archives/list/package-announce%40lists.fedoraproject.org/message/CGCFIFSIWUREEQQOZDZFBYKWZHXCWBZN/
- https://lists.fedoraproject.org/archives/list/package-announce%40lists.fedoraproject.org/message/KJMTVGDLA654HNCDGLCUEIP36SNJEKK7/
- https://seclists.org/bugtraq/2019/May/76
- http://lists.opensuse.org/opensuse-security-announce/2019-04/msg00094.html
- http://www.securityfocus.com/bid/107059
- https://usn.ubuntu.com/3923-1/
- https://www.debian.org/security/2019/dsa-4454
- https://bugzilla.redhat.com/show_bug.cgi?id=CVE-2019-3812
