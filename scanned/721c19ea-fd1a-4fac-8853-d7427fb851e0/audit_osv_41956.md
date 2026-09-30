# [C] netfs: Fix potential for tearing in ->remote_i_size and ->zero_point

## Summary
Severity: Critical
Advisory: CVE-2026-64160
Ecosystem: Linux
CVSS: 9.8 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H)
Published: 2026-07-19
Source: https://osv.dev/vulnerability/CVE-2026-64160
Type: osv

## Affected
- Linux: `Kernel` — affected >=5.18.0 <7.0.11

## Details
In the Linux kernel, the following vulnerability has been resolved:

netfs: Fix potential for tearing in ->remote_i_size and ->zero_point

Fix potential tearing in using ->remote_i_size and ->zero_point by copying
i_size_read() and i_size_write() and using the same seqcount as for i_size.

We need to make sure that netfslib and the filesystems that use it always
hold i_lock whilst updating any of the sizes to prevent i_size_seqcount
from getting corrupted.

## References
- https://git.kernel.org/stable/c/2c8f4742bb76117d735f92a3932d85239b16c494
- https://git.kernel.org/stable/c/55970f238d495517edc961d55c44c772594d0969
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/64xxx/CVE-2026-64160.json
- https://nvd.nist.gov/vuln/detail/CVE-2026-64160
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
