# [M] CVE-2021-38208

## Summary
Severity: Medium
Advisory: CVE-2021-38208
CVSS: 5.5 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:N/I:N/A:H)
Published: 2021-08-08
Source: https://osv.dev/vulnerability/CVE-2021-38208
Type: osv

## Details
net/nfc/llcp_sock.c in the Linux kernel before 5.12.10 allows local unprivileged users to cause a denial of service (NULL pointer dereference and BUG) by making a getsockname call after a certain type of failure of a bind call.

## References
- http://www.openwall.com/lists/oss-security/2021/08/17/1
- http://www.openwall.com/lists/oss-security/2021/08/17/2
- http://www.openwall.com/lists/oss-security/2021/08/24/2
- https://bugzilla.redhat.com/show_bug.cgi?id=1992810
- https://cdn.kernel.org/pub/linux/kernel/v5.x/ChangeLog-5.12.10
- https://github.com/torvalds/linux/commit/4ac06a1e013cf5fdd963317ffd3b968560f33bba
