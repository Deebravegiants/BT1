# [H] ksmbd: fix type confusion via race condition when using ipc_msg_send_request

## Summary
Severity: High
Advisory: CVE-2025-21947
Ecosystem: Linux
CVSS: 8.1 (CVSS:3.1/AV:N/AC:H/PR:N/UI:N/S:U/C:H/I:H/A:H)
Published: 2025-04-01
Source: https://osv.dev/vulnerability/CVE-2025-21947
Type: osv

## Affected
- Linux: `Kernel` — affected >=5.15.0 <6.1.131, >=6.2.0 <6.6.83, >=6.7.0 <6.12.19, >=6.13.0 <6.13.7

## Details
In the Linux kernel, the following vulnerability has been resolved:

ksmbd: fix type confusion via race condition when using ipc_msg_send_request

req->handle is allocated using ksmbd_acquire_id(&ipc_ida), based on
ida_alloc. req->handle from ksmbd_ipc_login_request and
FSCTL_PIPE_TRANSCEIVE ioctl can be same and it could lead to type confusion
between messages, resulting in access to unexpected parts of memory after
an incorrect delivery. ksmbd check type of ipc response but missing add
continue to check next ipc reponse.

## References
- https://git.kernel.org/stable/c/1e8833c03a38e1d5d5df6484e3f670a2fd38fb76
- https://git.kernel.org/stable/c/3cb2b2e41541fe6f9cc55ca22d4c0bd260498aea
- https://git.kernel.org/stable/c/6321bbda4244b93802d61cfe0887883aae322f4b
- https://git.kernel.org/stable/c/76861630b29e51373e73e7b00ad0d467b6941162
- https://git.kernel.org/stable/c/e2ff19f0b7a30e03516e6eb73b948e27a55bc9d2
- https://lists.debian.org/debian-lts-announce/2025/05/msg00045.html
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2025/21xxx/CVE-2025-21947.json
- https://nvd.nist.gov/vuln/detail/CVE-2025-21947
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
