# [H] ksmbd: fix slab-out-of-bounds in smb_strndup_from_utf16()

## Summary
Severity: High
Advisory: CVE-2024-26954
Ecosystem: Linux
CVSS: 8.1 (CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:H/I:N/A:H)
Published: 2024-05-01
Source: https://osv.dev/vulnerability/CVE-2024-26954
Type: osv

## Affected
- Linux: `Kernel` — affected >=5.15.0 <6.1.119, >=6.2.0 <6.6.32, >=6.7.0 <6.7.12, >=6.8.0 <6.8.3

## Details
In the Linux kernel, the following vulnerability has been resolved:

ksmbd: fix slab-out-of-bounds in smb_strndup_from_utf16()

If ->NameOffset of smb2_create_req is smaller than Buffer offset of
smb2_create_req, slab-out-of-bounds read can happen from smb2_open.
This patch set the minimum value of the name offset to the buffer offset
to validate name length of smb2_create_req().

## References
- https://git.kernel.org/stable/c/3b8da67191e938a63d2736dabb4ac5d337e5de57
- https://git.kernel.org/stable/c/4f97e6a9d62cb1fce82fbf4baff44b83221bc178
- https://git.kernel.org/stable/c/9e4937cbc150f9d5a9b5576e1922ef0b5ed2eb72
- https://git.kernel.org/stable/c/a80a486d72e20bd12c335bcd38b6e6f19356b0aa
- https://git.kernel.org/stable/c/d70c2e0904ab3715c5673fd45788a464a246d1db
- https://lists.debian.org/debian-lts-announce/2025/01/msg00001.html
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2024/26xxx/CVE-2024-26954.json
- https://nvd.nist.gov/vuln/detail/CVE-2024-26954
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
