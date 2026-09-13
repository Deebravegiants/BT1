# [H] ixgbevf: fix mailbox API compatibility by negotiating supported features

## Summary
Severity: High
Advisory: CVE-2025-40104
Ecosystem: Linux
CVSS: 7.8 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H)
Published: 2025-10-30
Source: https://osv.dev/vulnerability/CVE-2025-40104
Type: osv

## Affected
- Linux: `Kernel` — affected >=4.20.0 <6.1.158, >=6.2.0 <6.6.114, >=6.7.0 <6.12.55, >=6.13.0 <6.17.5

## Details
In the Linux kernel, the following vulnerability has been resolved:

ixgbevf: fix mailbox API compatibility by negotiating supported features

There was backward compatibility in the terms of mailbox API. Various
drivers from various OSes supporting 10G adapters from Intel portfolio
could easily negotiate mailbox API.

This convention has been broken since introducing API 1.4.
Commit 0062e7cc955e ("ixgbevf: add VF IPsec offload code") added support
for IPSec which is specific only for the kernel ixgbe driver. None of the
rest of the Intel 10G PF/VF drivers supports it. And actually lack of
support was not included in the IPSec implementation - there were no such
code paths. No possibility to negotiate support for the feature was
introduced along with introduction of the feature itself.

Commit 339f28964147 ("ixgbevf: Add support for new mailbox communication
between PF and VF") increasing API version to 1.5 did the same - it
introduced code supported specifically by the PF ESX driver. It altered API
version for the VF driver in the same time not touching the version
defined for the PF ixgbe driver. It led to additional discrepancies,
as the code provided within API 1.6 cannot be supported for Linux ixgbe
driver as it causes crashes.

The issue was noticed some time ago and mitigated by Jake within the commit
d0725312adf5 ("ixgbevf: stop attempting IPSEC offload on Mailbox API 1.5").
As a result we have regression for IPsec support and after increasing API
to version 1.6 ixgbevf driver stopped to support ESX MBX.

To fix this mess add new mailbox op asking PF driver about supported
features. Basing on a response determine whether to set support for IPSec
and ESX-specific enhanced mailbox.

New mailbox op, for compatibility purposes, must be added within new API
revision, as API version of OOT PF & VF drivers is already increased to
1.6 and doesn't incorporate features negotiate op.

Features negotiation mechanism gives possibility to be extended with new
features when needed in the future.

## References
- https://git.kernel.org/stable/c/2e0aab9ddaf1428602c78f12064cd1e6ffcc4d18
- https://git.kernel.org/stable/c/871ac1cd4ce4804defcb428cbb003fd84c415ff4
- https://git.kernel.org/stable/c/a376e29b1b196dc90b50df7e5e3947e3026300c4
- https://git.kernel.org/stable/c/a7075f501bd33c93570af759b6f4302ef0175168
- https://git.kernel.org/stable/c/bf580112ed61736c2645a893413a04732505d4b1
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2025/40xxx/CVE-2025-40104.json
- https://nvd.nist.gov/vuln/detail/CVE-2025-40104
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
