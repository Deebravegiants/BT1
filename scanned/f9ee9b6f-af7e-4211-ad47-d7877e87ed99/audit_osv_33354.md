# [C] tls: wait for pending async decryptions if tls_strp_msg_hold fails

## Summary
Severity: Critical
Advisory: CVE-2025-40176
Ecosystem: Linux
CVSS: 9.8 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H)
Published: 2025-11-12
Source: https://osv.dev/vulnerability/CVE-2025-40176
Type: osv

## Affected
- Linux: `Kernel` — affected >=6.0.0 <6.1.158, >=6.2.0 <6.6.114, >=6.7.0 <6.12.55, >=6.13.0 <6.17.5

## Details
In the Linux kernel, the following vulnerability has been resolved:

tls: wait for pending async decryptions if tls_strp_msg_hold fails

Async decryption calls tls_strp_msg_hold to create a clone of the
input skb to hold references to the memory it uses. If we fail to
allocate that clone, proceeding with async decryption can lead to
various issues (UAF on the skb, writing into userspace memory after
the recv() call has returned).

In this case, wait for all pending decryption requests.

## References
- https://git.kernel.org/stable/c/39dec4ea3daf77f684308576baf483b55ca7f160
- https://git.kernel.org/stable/c/4fc109d0ab196bd943b7451276690fb6bb48c2e0
- https://git.kernel.org/stable/c/9f83fd0c179e0f458e824e417f9d5ad53443f685
- https://git.kernel.org/stable/c/b8a6ff84abbcbbc445463de58704686011edc8e1
- https://git.kernel.org/stable/c/c61d4368197d65c4809d9271f3b85325a600586a
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2025/40xxx/CVE-2025-40176.json
- https://nvd.nist.gov/vuln/detail/CVE-2025-40176
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
