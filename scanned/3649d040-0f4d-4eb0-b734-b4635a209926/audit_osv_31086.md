# [C] gve: guard XDP xmit NDO on existence of xdp queues

## Summary
Severity: Critical
Advisory: CVE-2024-57932
Ecosystem: Linux
CVSS: 9.8 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H)
Published: 2025-01-21
Source: https://osv.dev/vulnerability/CVE-2024-57932
Type: osv

## Affected
- Linux: `Kernel` — affected >=6.4.0 <6.6.70, >=6.7.0 <6.12.9

## Details
In the Linux kernel, the following vulnerability has been resolved:

gve: guard XDP xmit NDO on existence of xdp queues

In GVE, dedicated XDP queues only exist when an XDP program is installed
and the interface is up. As such, the NDO XDP XMIT callback should
return early if either of these conditions are false.

In the case of no loaded XDP program, priv->num_xdp_queues=0 which can
cause a divide-by-zero error, and in the case of interface down,
num_xdp_queues remains untouched to persist XDP queue count for the next
interface up, but the TX pointer itself would be NULL.

The XDP xmit callback also needs to synchronize with a device
transitioning from open to close. This synchronization will happen via
the GVE_PRIV_FLAGS_NAPI_ENABLED bit along with a synchronize_net() call,
which waits for any RCU critical sections at call-time to complete.

## References
- https://git.kernel.org/stable/c/35f44eed5828cf1bc7e760d1993ed8549ba41c7b
- https://git.kernel.org/stable/c/cbe9eb2c39d09f3c8574febcfa39d8c09d0c7cb5
- https://git.kernel.org/stable/c/ff7c2dea9dd1a436fc79d6273adffdcc4a7ffea3
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2024/57xxx/CVE-2024-57932.json
- https://nvd.nist.gov/vuln/detail/CVE-2024-57932
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
