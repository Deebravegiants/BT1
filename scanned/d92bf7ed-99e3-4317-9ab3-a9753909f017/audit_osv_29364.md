# [H] net: txgbe: free isb resources at the right time

## Summary
Severity: High
Advisory: CVE-2024-42112
Ecosystem: Linux
CVSS: 7.8 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H)
Published: 2024-07-30
Source: https://osv.dev/vulnerability/CVE-2024-42112
Type: osv

## Affected
- Linux: `Kernel` — affected >=6.9.0 <6.9.9

## Details
In the Linux kernel, the following vulnerability has been resolved:

net: txgbe: free isb resources at the right time

When using MSI/INTx interrupt, the shared interrupts are still being
handled in the device remove routine, before free IRQs. So isb memory
is still read after it is freed. Thus move wx_free_isb_resources()
from txgbe_close() to txgbe_remove(). And fix the improper isb free
action in txgbe_open() error handling path.

## References
- https://git.kernel.org/stable/c/935124dd5883b5de68dc5a94f582480a10643dc9
- https://git.kernel.org/stable/c/efdc3f54299835ddef23bea651c753c4d467010b
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2024/42xxx/CVE-2024-42112.json
- https://nvd.nist.gov/vuln/detail/CVE-2024-42112
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
