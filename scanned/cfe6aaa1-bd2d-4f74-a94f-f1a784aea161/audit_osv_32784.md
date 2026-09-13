# [H] ksmbd: prevent out-of-bounds stream writes by validating *pos

## Summary
Severity: High
Advisory: CVE-2025-37947
Ecosystem: Linux
CVSS: 8.8 (CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H)
Published: 2025-05-20
Source: https://osv.dev/vulnerability/CVE-2025-37947
Type: osv

## Affected
- Linux: `Kernel` — affected >=5.15.0 <6.1.139, >=6.2.0 <6.6.91, >=6.7.0 <6.12.29, >=6.13.0 <6.14.7

## Details
In the Linux kernel, the following vulnerability has been resolved:

ksmbd: prevent out-of-bounds stream writes by validating *pos

ksmbd_vfs_stream_write() did not validate whether the write offset
(*pos) was within the bounds of the existing stream data length (v_len).
If *pos was greater than or equal to v_len, this could lead to an
out-of-bounds memory write.

This patch adds a check to ensure *pos is less than v_len before
proceeding. If the condition fails, -EINVAL is returned.

## References
- https://git.kernel.org/stable/c/04c8a38c60346bb5a7c49b276de7233f703ce9cb
- https://git.kernel.org/stable/c/0ca6df4f40cf4c32487944aaf48319cb6c25accc
- https://git.kernel.org/stable/c/7f61da79df86fd140c7768e668ad846bfa7ec8e1
- https://git.kernel.org/stable/c/d62ba16563a86aae052f96d270b3b6f78fca154c
- https://git.kernel.org/stable/c/e6356499fd216ed6343ae0363f4c9303f02c5034
- https://lists.debian.org/debian-lts-announce/2025/08/msg00010.html
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2025/37xxx/CVE-2025-37947.json
- https://nvd.nist.gov/vuln/detail/CVE-2025-37947
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
- https://github.com/doyensec/KSMBD-CVE-2025-37947/blob/main/CVE-2025-37947.c
