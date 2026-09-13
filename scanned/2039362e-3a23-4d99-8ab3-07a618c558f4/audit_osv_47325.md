# [M] CVE-2016-2550

## Summary
Severity: Medium
Advisory: CVE-2016-2550
CVSS: 5.5 (CVSS:3.0/AV:L/AC:L/PR:L/UI:N/S:U/C:N/I:N/A:H)
Published: 2016-04-27
Source: https://osv.dev/vulnerability/CVE-2016-2550
Type: osv

## Details
The Linux kernel before 4.5 allows local users to bypass file-descriptor limits and cause a denial of service (memory consumption) by leveraging incorrect tracking of descriptor ownership and sending each descriptor over a UNIX socket before closing it. NOTE: this vulnerability exists because of an incorrect fix for CVE-2013-4312.

## References
- http://www.openwall.com/lists/oss-security/2016/02/23/2
- http://www.ubuntu.com/usn/USN-2947-1
- http://www.ubuntu.com/usn/USN-2947-2
- http://www.ubuntu.com/usn/USN-2947-3
- http://www.ubuntu.com/usn/USN-2948-1
- http://git.kernel.org/cgit/linux/kernel/git/torvalds/linux.git/commit/?id=415e3d3e90ce9e18727e8843ae343eda5a58fad6
- http://www.debian.org/security/2016/dsa-3503
- http://www.oracle.com/technetwork/security-advisory/cpujan2018-3236628.html
- http://www.ubuntu.com/usn/USN-2946-1
- http://www.ubuntu.com/usn/USN-2946-2
- http://www.ubuntu.com/usn/USN-2948-2
- http://www.ubuntu.com/usn/USN-2949-1
- https://bugzilla.redhat.com/show_bug.cgi?id=1311517
- https://github.com/torvalds/linux/commit/415e3d3e90ce9e18727e8843ae343eda5a58fad6
