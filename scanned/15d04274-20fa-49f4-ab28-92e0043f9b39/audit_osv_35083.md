# [H] ksmbd: close accepted socket when per-IP limit rejects connection

## Summary
Severity: High
Advisory: CVE-2025-68246
Ecosystem: Linux
CVSS: 7.5 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:H)
Published: 2025-12-16
Source: https://osv.dev/vulnerability/CVE-2025-68246
Type: osv

## Affected
- Linux: `Kernel` — affected >=5.15.0 <6.1.159, >=6.2.0 <6.6.117, >=6.7.0 <6.12.59, >=6.13.0 <6.17.9

## Details
In the Linux kernel, the following vulnerability has been resolved:

ksmbd: close accepted socket when per-IP limit rejects connection

When the per-IP connection limit is exceeded in ksmbd_kthread_fn(),
the code sets ret = -EAGAIN and continues the accept loop without
closing the just-accepted socket. That leaks one socket per rejected
attempt from a single IP and enables a trivial remote DoS.

Release client_sk before continuing.

This bug was found with ZeroPath.

## References
- https://git.kernel.org/stable/c/35521b5a7e8a184548125f4530552101236dcda1
- https://git.kernel.org/stable/c/4587a7826be1ae0190dba10ff70b46bb0e3bc7d3
- https://git.kernel.org/stable/c/5746b2a0f5eb3d79667b3c51fe849bd62464220e
- https://git.kernel.org/stable/c/7a3c7154d5fc05956a8ad9e72ecf49e21555bfca
- https://git.kernel.org/stable/c/98a5fd31cbf72d46bf18e50b3ab0ce86d5f319a9
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2025/68xxx/CVE-2025-68246.json
- https://nvd.nist.gov/vuln/detail/CVE-2025-68246
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
