# [H] fs/ntfs3: Update log->page_{mask,bits} if log->page_size changed

## Summary
Severity: High
Advisory: CVE-2024-42299
Ecosystem: Linux
CVSS: 7.8 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H)
Published: 2024-08-17
Source: https://osv.dev/vulnerability/CVE-2024-42299
Type: osv

## Affected
- Linux: `Kernel` — affected >=5.15.0 <5.15.165, >=5.16.0 <6.1.103, >=6.2.0 <6.6.44, >=6.7.0 <6.10.3

## Details
In the Linux kernel, the following vulnerability has been resolved:

fs/ntfs3: Update log->page_{mask,bits} if log->page_size changed

If an NTFS file system is mounted to another system with different
PAGE_SIZE from the original system, log->page_size will change in
log_replay(), but log->page_{mask,bits} don't change correspondingly.
This will cause a panic because "u32 bytes = log->page_size - page_off"
will get a negative value in the later read_log_page().

## References
- https://git.kernel.org/stable/c/0484adcb5fbcadd9ba0fd4485c42630f72e97da9
- https://git.kernel.org/stable/c/0a4ae2644e2a3b3b219aad9639fb2b0691d08420
- https://git.kernel.org/stable/c/2cac0df3324b5e287d8020bc0708f7d2dec88a6f
- https://git.kernel.org/stable/c/2fef55d8f78383c8e6d6d4c014b9597375132696
- https://git.kernel.org/stable/c/b90ceffdc975502bc085ce8e79c6adeff05f9521
- https://lists.debian.org/debian-lts-announce/2025/01/msg00001.html
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2024/42xxx/CVE-2024-42299.json
- https://nvd.nist.gov/vuln/detail/CVE-2024-42299
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
