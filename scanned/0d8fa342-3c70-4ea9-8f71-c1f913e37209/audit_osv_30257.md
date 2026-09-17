# [H] fs/ntfs3: Check if more than chunk-size bytes are written

## Summary
Severity: High
Advisory: CVE-2024-50247
Ecosystem: Linux
CVSS: 7.3 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:H/I:L/A:H)
Published: 2024-11-09
Source: https://osv.dev/vulnerability/CVE-2024-50247
Type: osv

## Affected
- Linux: `Kernel` — affected >=5.15.0 <5.15.171, >=5.16.0 <6.1.116, >=6.2.0 <6.6.60, >=6.7.0 <6.11.7

## Details
In the Linux kernel, the following vulnerability has been resolved:

fs/ntfs3: Check if more than chunk-size bytes are written

A incorrectly formatted chunk may decompress into
more than LZNT_CHUNK_SIZE bytes and a index out of bounds
will occur in s_max_off.

## References
- https://git.kernel.org/stable/c/1b6bc5f7212181093b6c5310eea216fc09c721a9
- https://git.kernel.org/stable/c/4a4727bc582832f354e0d3d49838a401a28ae25e
- https://git.kernel.org/stable/c/5f21e3e60982cd7353998b4f59f052134fd47d64
- https://git.kernel.org/stable/c/9931122d04c6d431b2c11b5bb7b10f28584067f0
- https://git.kernel.org/stable/c/e5ae7859008688626b4d2fa6139eeaa08e255053
- https://lists.debian.org/debian-lts-announce/2025/01/msg00001.html
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2024/50xxx/CVE-2024-50247.json
- https://nvd.nist.gov/vuln/detail/CVE-2024-50247
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
