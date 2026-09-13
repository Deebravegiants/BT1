# [H] s390/ctcm: Fix double-kfree

## Summary
Severity: High
Advisory: CVE-2025-40253
Ecosystem: Linux
CVSS: 8.8 (CVSS:3.1/AV:A/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H)
Published: 2025-12-04
Source: https://osv.dev/vulnerability/CVE-2025-40253
Type: osv

## Affected
- Linux: `Kernel` — affected >=0 <5.4.302, >=5.5.0 <5.10.247, >=5.11.0 <5.15.197, >=5.16.0 <6.1.159, >=5.18.0 <6.6.118, >=6.2.0 <6.12.60, >=6.7.0 <6.17.10

## Details
In the Linux kernel, the following vulnerability has been resolved:

s390/ctcm: Fix double-kfree

The function 'mpc_rcvd_sweep_req(mpcginfo)' is called conditionally
from function 'ctcmpc_unpack_skb'. It frees passed mpcginfo.
After that a call to function 'kfree' in function 'ctcmpc_unpack_skb'
frees it again.

Remove 'kfree' call in function 'mpc_rcvd_sweep_req(mpcginfo)'.

Bug detected by the clang static analyzer.

## References
- https://git.kernel.org/stable/c/06f1dd1de0d33dbfbd2e1fc9fc57d8895f730de2
- https://git.kernel.org/stable/c/3b177b2ded563df16f6d5920671ffcfe5915d472
- https://git.kernel.org/stable/c/43096dab8cc60fc39133205fd149a54d3acebea8
- https://git.kernel.org/stable/c/6bf8ccaabce8cebb6cb1f255c93d0acdfe95c17a
- https://git.kernel.org/stable/c/7616e2eee679746d526c7f5befd4eedb995935b5
- https://git.kernel.org/stable/c/7ff76f8dc6b550f8d16487bf3cebc278be720b5c
- https://git.kernel.org/stable/c/b9dbfb1b5699f9f1e4991f96741bdf9047147589
- https://git.kernel.org/stable/c/da02a1824884d6c84c5e5b5ac373b0c9e3288ec2
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2025/40xxx/CVE-2025-40253.json
- https://nvd.nist.gov/vuln/detail/CVE-2025-40253
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
