# [H] SUNRPC: lock against ->sock changing during sysfs read

## Summary
Severity: High
Advisory: CVE-2022-48816
Ecosystem: Linux
CVSS: 7.8 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H)
Published: 2024-07-16
Source: https://osv.dev/vulnerability/CVE-2022-48816
Type: osv

## Affected
- Linux: `Kernel` — affected >=5.14.0 <5.15.209, >=5.16.0 <5.16.10

## Details
In the Linux kernel, the following vulnerability has been resolved:

SUNRPC: lock against ->sock changing during sysfs read

->sock can be set to NULL asynchronously unless ->recv_mutex is held.
So it is important to hold that mutex.  Otherwise a sysfs read can
trigger an oops.
Commit 17f09d3f619a ("SUNRPC: Check if the xprt is connected before
handling sysfs reads") appears to attempt to fix this problem, but it
only narrows the race window.

## References
- https://git.kernel.org/stable/c/9482ab4540f5bcc869b44c067ae99b5fca16bd07
- https://git.kernel.org/stable/c/b49ea673e119f59c71645e2f65b3ccad857c90ee
- https://git.kernel.org/stable/c/fdc42287ae3f8a35cc2098307f52d7864b4bc8ed
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2022/48xxx/CVE-2022-48816.json
- https://nvd.nist.gov/vuln/detail/CVE-2022-48816
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
