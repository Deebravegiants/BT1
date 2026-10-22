# [M] CVE-2016-2085

## Summary
Severity: Medium
Advisory: CVE-2016-2085
CVSS: 5.5 (CVSS:3.0/AV:L/AC:L/PR:L/UI:N/S:U/C:N/I:H/A:N)
Published: 2016-04-27
Source: https://osv.dev/vulnerability/CVE-2016-2085
Type: osv

## Details
The evm_verify_hmac function in security/integrity/evm/evm_main.c in the Linux kernel before 4.5 does not properly copy data, which makes it easier for local users to forge MAC values via a timing side-channel attack.

## References
- https://security-tracker.debian.org/tracker/CVE-2016-2085
- https://people.canonical.com/~ubuntu-security/cve/2016/CVE-2016-2085.html
- http://git.kernel.org/cgit/linux/kernel/git/torvalds/linux.git/commit/?id=613317bd212c585c20796c10afe5daaa95d4b0a1
- http://www.ubuntu.com/usn/USN-2946-1
- http://www.ubuntu.com/usn/USN-2947-3
- http://www.ubuntu.com/usn/USN-2946-2
- http://www.ubuntu.com/usn/USN-2947-1
- http://www.ubuntu.com/usn/USN-2947-2
- http://www.ubuntu.com/usn/USN-2948-1
- http://www.ubuntu.com/usn/USN-2948-2
- http://www.ubuntu.com/usn/USN-2949-1
- https://bugzilla.redhat.com/show_bug.cgi?id=1324867
- https://github.com/torvalds/linux/commit/613317bd212c585c20796c10afe5daaa95d4b0a1
