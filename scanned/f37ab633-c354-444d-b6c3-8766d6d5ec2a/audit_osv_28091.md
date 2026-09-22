# [H] nvme: fix reconnection fail due to reserved tag allocation

## Summary
Severity: High
Advisory: CVE-2024-27435
Ecosystem: Linux
CVSS: 7.5 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:H)
Published: 2024-05-17
Source: https://osv.dev/vulnerability/CVE-2024-27435
Type: osv

## Affected
- Linux: `Kernel` — affected >=5.12.0 <6.1.83, >=6.2.0 <6.6.23, >=6.7.0 <6.7.11, >=6.8.0 <6.8.2

## Details
In the Linux kernel, the following vulnerability has been resolved:

nvme: fix reconnection fail due to reserved tag allocation

We found a issue on production environment while using NVMe over RDMA,
admin_q reconnect failed forever while remote target and network is ok.
After dig into it, we found it may caused by a ABBA deadlock due to tag
allocation. In my case, the tag was hold by a keep alive request
waiting inside admin_q, as we quiesced admin_q while reset ctrl, so the
request maked as idle and will not process before reset success. As
fabric_q shares tagset with admin_q, while reconnect remote target, we
need a tag for connect command, but the only one reserved tag was held
by keep alive command which waiting inside admin_q. As a result, we
failed to reconnect admin_q forever. In order to fix this issue, I
think we should keep two reserved tags for admin queue.

## References
- https://git.kernel.org/stable/c/149afee5c7418ec5db9d7387b9c9a5c1eb7ea2a8
- https://git.kernel.org/stable/c/262da920896e2f2ab0e3947d9dbee0aa09045818
- https://git.kernel.org/stable/c/6851778504cdb49431809b4ba061903d5f592c96
- https://git.kernel.org/stable/c/de105068fead55ed5c07ade75e9c8e7f86a00d1d
- https://git.kernel.org/stable/c/ff2f90f88d78559802466ad1c84ac5bda4416b3a
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2024/27xxx/CVE-2024-27435.json
- https://nvd.nist.gov/vuln/detail/CVE-2024-27435
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
