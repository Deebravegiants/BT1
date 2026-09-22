# [H] vsock: Fix transport_* TOCTOU

## Summary
Severity: High
Advisory: CVE-2025-38461
Ecosystem: Linux
CVSS: 7.0 (CVSS:3.1/AV:L/AC:H/PR:L/UI:N/S:U/C:H/I:H/A:H)
Published: 2025-07-25
Source: https://osv.dev/vulnerability/CVE-2025-38461
Type: osv

## Affected
- Linux: `Kernel` — affected >=5.5.0 <5.10.240, >=5.11.0 <5.15.189, >=5.16.0 <6.1.146, >=6.2.0 <6.6.99, >=6.7.0 <6.12.39, >=6.13.0 <6.15.7

## Details
In the Linux kernel, the following vulnerability has been resolved:

vsock: Fix transport_* TOCTOU

Transport assignment may race with module unload. Protect new_transport
from becoming a stale pointer.

This also takes care of an insecure call in vsock_use_local_transport();
add a lockdep assert.

BUG: unable to handle page fault for address: fffffbfff8056000
Oops: Oops: 0000 [#1] SMP KASAN
RIP: 0010:vsock_assign_transport+0x366/0x600
Call Trace:
 vsock_connect+0x59c/0xc40
 __sys_connect+0xe8/0x100
 __x64_sys_connect+0x6e/0xc0
 do_syscall_64+0x92/0x1c0
 entry_SYSCALL_64_after_hwframe+0x4b/0x53

## References
- https://git.kernel.org/stable/c/36a439049b34cca0b3661276049b84a1f76cc21a
- https://git.kernel.org/stable/c/687aa0c5581b8d4aa87fd92973e4ee576b550cdf
- https://git.kernel.org/stable/c/7b73bddf54777fb62d4d8c7729d0affe6df04477
- https://git.kernel.org/stable/c/8667e8d0eb46bc54fdae30ba2f4786407d3d88eb
- https://git.kernel.org/stable/c/9ce53e744f18e73059d3124070e960f3aa9902bf
- https://git.kernel.org/stable/c/9d24bb6780282b0255b9929abe5e8f98007e2c6e
- https://git.kernel.org/stable/c/ae2c712ba39c7007de63cb0c75b51ce1caaf1da5
- https://lists.debian.org/debian-lts-announce/2025/10/msg00007.html
- https://lists.debian.org/debian-lts-announce/2025/10/msg00008.html
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2025/38xxx/CVE-2025-38461.json
- https://nvd.nist.gov/vuln/detail/CVE-2025-38461
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
