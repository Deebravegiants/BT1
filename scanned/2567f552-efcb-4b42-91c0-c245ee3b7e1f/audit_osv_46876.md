# [M] CVE-2015-7550

## Summary
Severity: Medium
Advisory: CVE-2015-7550
CVSS: 5.5 (CVSS:3.0/AV:L/AC:L/PR:L/UI:N/S:U/C:N/I:N/A:H)
Published: 2016-02-08
Source: https://osv.dev/vulnerability/CVE-2015-7550
Type: osv

## Details
The keyctl_read_key function in security/keys/keyctl.c in the Linux kernel before 4.3.4 does not properly use a semaphore, which allows local users to cause a denial of service (NULL pointer dereference and system crash) or possibly have unspecified other impact via a crafted application that leverages a race condition between keyctl_revoke and keyctl_read calls.

## References
- http://git.kernel.org/cgit/linux/kernel/git/torvalds/linux.git/commit/?id=b4a1b4f5047e4f54e194681125c74c0aa64d637d
- http://www.debian.org/security/2016/dsa-3434
- http://www.kernel.org/pub/linux/kernel/v4.x/ChangeLog-4.3.4
- http://www.ubuntu.com/usn/USN-2888-1
- http://www.ubuntu.com/usn/USN-2890-1
- http://www.ubuntu.com/usn/USN-2890-2
- http://www.ubuntu.com/usn/USN-2890-3
- http://www.ubuntu.com/usn/USN-2911-1
- http://www.ubuntu.com/usn/USN-2911-2
- https://github.com/torvalds/linux/commit/b4a1b4f5047e4f54e194681125c74c0aa64d637d
- https://bugzilla.redhat.com/show_bug.cgi?id=1291197
- http://lists.opensuse.org/opensuse-security-announce/2016-03/msg00094.html
- http://lists.opensuse.org/opensuse-security-announce/2016-04/msg00045.html
- http://lists.opensuse.org/opensuse-security-announce/2016-08/msg00038.html
- http://www.securityfocus.com/bid/79903
- https://security-tracker.debian.org/tracker/CVE-2015-7550
