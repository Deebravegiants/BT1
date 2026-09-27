# [H] ksmbd: fix out-of-bound read in smb2_write

## Summary
Severity: High
Advisory: CVE-2023-3865
Ecosystem: Linux
CVSS: 8.1 (CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:H/I:N/A:H)
Published: 2025-08-16
Source: https://osv.dev/vulnerability/CVE-2023-3865
Type: osv

## Affected
- Linux: `Kernel` — affected >=5.15.0 <5.15.121, >=5.16.0 <6.1.36, >=6.2.0 <6.3.10

## Details
In the Linux kernel, the following vulnerability has been resolved:

ksmbd: fix out-of-bound read in smb2_write

ksmbd_smb2_check_message doesn't validate hdr->NextCommand. If
->NextCommand is bigger than Offset + Length of smb2 write, It will
allow oversized smb2 write length. It will cause OOB read in smb2_write.

## References
- https://git.kernel.org/stable/c/3813eee5154d6a4c5875cb4444cb2b63bac8947f
- https://git.kernel.org/stable/c/58a9c41064df27632e780c5a3ae3e0e4284957d1
- https://git.kernel.org/stable/c/5fe7f7b78290638806211046a99f031ff26164e1
- https://git.kernel.org/stable/c/c86211159bc3178b891e0d60e586a32c7b6a231b
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2023/3xxx/CVE-2023-3865.json
- https://nvd.nist.gov/vuln/detail/CVE-2023-3865
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
