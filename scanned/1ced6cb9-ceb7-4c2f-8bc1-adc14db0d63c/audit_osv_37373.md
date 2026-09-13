# [H] ksmbd: fix potencial OOB in get_file_all_info() for compound requests

## Summary
Severity: High
Advisory: CVE-2026-31433
Ecosystem: Linux
CVSS: 8.8 (CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H)
Published: 2026-04-22
Source: https://osv.dev/vulnerability/CVE-2026-31433
Type: osv

## Affected
- Linux: `Kernel` — affected >=0 <5.15.203, >=5.16.0 <6.1.168, >=6.2.0 <6.6.131, >=6.6.0 <6.12.80, >=6.7.0 <6.18.21, >=6.13.0 <6.19.11

## Details
In the Linux kernel, the following vulnerability has been resolved:

ksmbd: fix potencial OOB in get_file_all_info() for compound requests

When a compound request consists of QUERY_DIRECTORY + QUERY_INFO
(FILE_ALL_INFORMATION) and the first command consumes nearly the entire
max_trans_size, get_file_all_info() would blindly call smbConvertToUTF16()
with PATH_MAX, causing out-of-bounds write beyond the response buffer.
In get_file_all_info(), there was a missing validation check for
the client-provided OutputBufferLength before copying the filename into
FileName field of the smb2_file_all_info structure.
If the filename length exceeds the available buffer space, it could lead to
potential buffer overflows or memory corruption during smbConvertToUTF16
conversion. This calculating the actual free buffer size using
smb2_calc_max_out_buf_len() and returning -EINVAL if the buffer is
insufficient and updating smbConvertToUTF16 to use the actual filename
length (clamped by PATH_MAX) to ensure a safe copy operation.

## References
- https://git.kernel.org/stable/c/358cdaa1f7fbf2712cb4c5f6b59cb9a5c673c5fe
- https://git.kernel.org/stable/c/3a852f9d1c981fb14f6bf4e24999e0ea8088a7d7
- https://git.kernel.org/stable/c/4cca3eff2099b18672934a39cee70aed835d652c
- https://git.kernel.org/stable/c/7aec5a769d2356cbf344d85bcfd36de592ac96a5
- https://git.kernel.org/stable/c/9d7032851d6f5adbe2739601ca456c0ad3b422f0
- https://git.kernel.org/stable/c/b0cd9725fe2bcc9f37d096b132318a9060373f5d
- https://git.kernel.org/stable/c/beef2634f81f1c086208191f7228bce1d366493d
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/31xxx/CVE-2026-31433.json
- https://nvd.nist.gov/vuln/detail/CVE-2026-31433
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
