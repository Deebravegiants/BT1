# [M] CVE-2016-2187

## Summary
Severity: Medium
Advisory: CVE-2016-2187
CVSS: 4.6 (CVSS:3.0/AV:P/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:H)
Published: 2016-05-02
Source: https://osv.dev/vulnerability/CVE-2016-2187
Type: osv

## Details
The gtco_probe function in drivers/input/tablet/gtco.c in the Linux kernel through 4.5.2 allows physically proximate attackers to cause a denial of service (NULL pointer dereference and system crash) via a crafted endpoints value in a USB device descriptor.

## References
- http://lists.opensuse.org/opensuse-security-announce/2016-08/msg00007.html
- http://www.securityfocus.com/bid/85425
- http://lists.opensuse.org/opensuse-security-announce/2016-06/msg00052.html
- http://www.debian.org/security/2016/dsa-3607
- http://www.ubuntu.com/usn/USN-3004-1
- http://www.ubuntu.com/usn/USN-2989-1
- http://www.ubuntu.com/usn/USN-2997-1
- http://www.ubuntu.com/usn/USN-3003-1
- http://www.ubuntu.com/usn/USN-2998-1
- http://www.ubuntu.com/usn/USN-3001-1
- http://www.ubuntu.com/usn/USN-3002-1
- http://www.ubuntu.com/usn/USN-3006-1
- http://www.ubuntu.com/usn/USN-2996-1
- http://www.ubuntu.com/usn/USN-3000-1
- http://www.ubuntu.com/usn/USN-3005-1
- http://www.ubuntu.com/usn/USN-3007-1
- https://bugzilla.redhat.com/show_bug.cgi?id=1317017
- https://github.com/torvalds/linux/commit/162f98dea487206d9ab79fc12ed64700667a894d
- http://git.kernel.org/cgit/linux/kernel/git/torvalds/linux.git/commit/?id=162f98dea487206d9ab79fc12ed64700667a894d
