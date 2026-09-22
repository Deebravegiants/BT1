# [M] CVE-2016-2184

## Summary
Severity: Medium
Advisory: CVE-2016-2184
CVSS: 4.6 (CVSS:3.0/AV:P/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:H)
Published: 2016-04-27
Source: https://osv.dev/vulnerability/CVE-2016-2184
Type: osv

## Details
The create_fixed_stream_quirk function in sound/usb/quirks.c in the snd-usb-audio driver in the Linux kernel before 4.5.1 allows physically proximate attackers to cause a denial of service (NULL pointer dereference or double free, and system crash) via a crafted endpoints value in a USB device descriptor.

## References
- http://lists.opensuse.org/opensuse-security-announce/2016-08/msg00038.html
- http://www.securityfocus.com/bid/84340
- http://lists.opensuse.org/opensuse-security-announce/2016-04/msg00019.html
- https://source.android.com/security/bulletin/2016-11-01.html
- https://www.exploit-db.com/exploits/39555/
- http://lists.opensuse.org/opensuse-security-announce/2016-04/msg00015.html
- http://www.ubuntu.com/usn/USN-2968-2
- http://www.ubuntu.com/usn/USN-2969-1
- http://www.ubuntu.com/usn/USN-2971-2
- http://www.ubuntu.com/usn/USN-2997-1
- https://github.com/torvalds/linux/commit/0f886ca12765d20124bd06291c82951fd49a33be
- http://git.kernel.org/cgit/linux/kernel/git/torvalds/linux.git/commit/?id=0f886ca12765d20124bd06291c82951fd49a33be
- http://lists.opensuse.org/opensuse-security-announce/2016-06/msg00052.html
- http://lists.opensuse.org/opensuse-security-announce/2016-06/msg00054.html
- http://www.ubuntu.com/usn/USN-2968-1
- http://www.ubuntu.com/usn/USN-2970-1
- http://www.ubuntu.com/usn/USN-2996-1
- http://seclists.org/bugtraq/2016/Mar/102
- http://www.ubuntu.com/usn/USN-2971-1
- http://www.ubuntu.com/usn/USN-2971-3
