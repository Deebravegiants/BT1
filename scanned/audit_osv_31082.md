# [H] ksmbd: fix a missing return value check bug

## Summary
Severity: High
Advisory: CVE-2024-57925
Ecosystem: Linux
CVSS: 7.1 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:N/I:H/A:H)
Published: 2025-01-19
Source: https://osv.dev/vulnerability/CVE-2024-57925
Type: osv

## Affected
- Linux: `Kernel` — affected >=0 <5.15.177, >=5.16.0 <6.1.125, >=6.2.0 <6.6.72, >=6.6.0 <6.12.10

## Details
In the Linux kernel, the following vulnerability has been resolved:

ksmbd: fix a missing return value check bug

In the smb2_send_interim_resp(), if ksmbd_alloc_work_struct()
fails to allocate a node, it returns a NULL pointer to the
in_work pointer. This can lead to an illegal memory write of
in_work->response_buf when allocate_interim_rsp_buf() attempts
to perform a kzalloc() on it.

To address this issue, incorporating a check for the return
value of ksmbd_alloc_work_struct() ensures that the function
returns immediately upon allocation failure, thereby preventing
the aforementioned illegal memory access.

## References
- https://git.kernel.org/stable/c/271ae0edbfc942795c162e6cf20d2bc02bd7fde4
- https://git.kernel.org/stable/c/2976e91a3e569cf2c92c9f71512c0ab1312fe965
- https://git.kernel.org/stable/c/4c16e1cadcbcaf3c82d5fc310fbd34d0f5d0db7c
- https://git.kernel.org/stable/c/781c743e18bfd9b7dc0383f036ae952bd1486f21
- https://git.kernel.org/stable/c/ee7e40f7fb17f08a8cbae50553e5c2e10ae32fce
- https://lists.debian.org/debian-lts-announce/2025/03/msg00001.html
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2024/57xxx/CVE-2024-57925.json
- https://nvd.nist.gov/vuln/detail/CVE-2024-57925
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
