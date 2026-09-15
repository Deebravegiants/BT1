# [H] net/mlx5e: Fix race condition during IPSec ESN update

## Summary
Severity: High
Advisory: CVE-2026-23440
Ecosystem: Linux
CVSS: 7.5 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:H)
Published: 2026-04-03
Source: https://osv.dev/vulnerability/CVE-2026-23440
Type: osv

## Affected
- Linux: `Kernel` — affected >=6.4.0 <6.6.130, >=6.7.0 <6.12.78, >=6.13.0 <6.18.20, >=6.19.0 <6.19.10

## Details
In the Linux kernel, the following vulnerability has been resolved:

net/mlx5e: Fix race condition during IPSec ESN update

In IPSec full offload mode, the device reports an ESN (Extended
Sequence Number) wrap event to the driver. The driver validates this
event by querying the IPSec ASO and checking that the esn_event_arm
field is 0x0, which indicates an event has occurred. After handling
the event, the driver must re-arm the context by setting esn_event_arm
back to 0x1.

A race condition exists in this handling path. After validating the
event, the driver calls mlx5_accel_esp_modify_xfrm() to update the
kernel's xfrm state. This function temporarily releases and
re-acquires the xfrm state lock.

So, need to acknowledge the event first by setting esn_event_arm to
0x1. This prevents the driver from reprocessing the same ESN update if
the hardware sends events for other reason. Since the next ESN update
only occurs after nearly 2^31 packets are received, there's no risk of
missing an update, as it will happen long after this handling has
finished.

Processing the event twice causes the ESN high-order bits (esn_msb) to
be incremented incorrectly. The driver then programs the hardware with
this invalid ESN state, which leads to anti-replay failures and a
complete halt of IPSec traffic.

Fix this by re-arming the ESN event immediately after it is validated,
before calling mlx5_accel_esp_modify_xfrm(). This ensures that any
spurious, duplicate events are correctly ignored, closing the race
window.

## References
- https://git.kernel.org/stable/c/2051c709dce92da3550040aa7949cd5a9c89b14e
- https://git.kernel.org/stable/c/3dffc083292e6872787bd7e34b957627622f9af4
- https://git.kernel.org/stable/c/8d625c15471fb8780125eaef682983a96af77bdc
- https://git.kernel.org/stable/c/96c9c25b74686ac2de15921c9ad30c5ef13af8cd
- https://git.kernel.org/stable/c/beb6e2e5976a128b0cccf10d158124422210c5ef
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/23xxx/CVE-2026-23440.json
- https://nvd.nist.gov/vuln/detail/CVE-2026-23440
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
