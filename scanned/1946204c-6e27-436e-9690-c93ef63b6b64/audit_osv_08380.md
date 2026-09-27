# [M] CVE-2016-2782

## Summary
Severity: Medium
Advisory: CVE-2016-2782
CVSS: 4.6 (CVSS:3.1/AV:P/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:H)
Published: 2016-04-27
Source: https://osv.dev/vulnerability/CVE-2016-2782
Type: osv

## Details
The treo_attach function in drivers/usb/serial/visor.c in the Linux kernel before 4.5 allows physically proximate attackers to cause a denial of service (NULL pointer dereference and system crash) or possibly have unspecified other impact by inserting a USB device that lacks a (1) bulk-in or (2) interrupt-in endpoint.

## References
- http://lists.opensuse.org/opensuse-security-announce/2016-08/msg00038.html
- http://www.ubuntu.com/usn/USN-2929-1
- http://www.ubuntu.com/usn/USN-2948-1
- http://www.ubuntu.com/usn/USN-2967-2
- https://www.exploit-db.com/exploits/39539/
- http://lists.opensuse.org/opensuse-security-announce/2016-06/msg00054.html
- http://www.ubuntu.com/usn/USN-2930-2
- http://www.ubuntu.com/usn/USN-2932-1
- http://www.ubuntu.com/usn/USN-2948-2
- http://lists.opensuse.org/opensuse-security-announce/2016-04/msg00019.html
- http://lists.opensuse.org/opensuse-security-announce/2016-06/msg00059.html
- http://www.ubuntu.com/usn/USN-2930-1
- http://www.ubuntu.com/usn/USN-2930-3
- http://www.ubuntu.com/usn/USN-2967-1
- http://lists.opensuse.org/opensuse-security-announce/2016-06/msg00052.html
- http://lists.opensuse.org/opensuse-security-announce/2016-07/msg00005.html
- http://www.openwall.com/lists/oss-security/2016/02/28/9
- http://www.ubuntu.com/usn/USN-2929-2
- https://bugzilla.redhat.com/show_bug.cgi?id=1312670
- https://github.com/torvalds/linux/commit/cac9b50b0d75a1d50d6c056ff65c005f3224c8e0
