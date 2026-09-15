# [M] net: micrel: Fix receiving the timestamp in the frame for lan8841

## Summary
Severity: Medium
Advisory: CVE-2024-38593
Ecosystem: Linux
CVSS: 5.5 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:N/I:N/A:H)
Published: 2024-06-19
Source: https://osv.dev/vulnerability/CVE-2024-38593
Type: osv

## Affected
- Linux: `Kernel` — affected >=6.5.0 <6.6.33, >=6.7.0 <6.8.12, >=6.9.0 <6.9.3

## Details
In the Linux kernel, the following vulnerability has been resolved:

net: micrel: Fix receiving the timestamp in the frame for lan8841

The blamed commit started to use the ptp workqueue to get the second
part of the timestamp. And when the port was set down, then this
workqueue is stopped. But if the config option NETWORK_PHY_TIMESTAMPING
is not enabled, then the ptp_clock is not initialized so then it would
crash when it would try to access the delayed work.
So then basically by setting up and then down the port, it would crash.
The fix consists in checking if the ptp_clock is initialized and only
then cancel the delayed work.

## References
- https://git.kernel.org/stable/c/3ddf170e4a604f5d4d9459a36993f5e92b53e8b0
- https://git.kernel.org/stable/c/3fd4282d5f25c3c97fef3ef0b89b82ef4e2bc975
- https://git.kernel.org/stable/c/64a47cf634ae44e92be24ebc982410841093bd7b
- https://git.kernel.org/stable/c/aea27a92a41dae14843f92c79e9e42d8f570105c
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2024/38xxx/CVE-2024-38593.json
- https://nvd.nist.gov/vuln/detail/CVE-2024-38593
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
