# [H] lan966x: Fix crash when adding interface under a lag

## Summary
Severity: High
Advisory: CVE-2024-26723
Ecosystem: Linux
CVSS: 7.8 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H)
Published: 2024-04-03
Source: https://osv.dev/vulnerability/CVE-2024-26723
Type: osv

## Affected
- Linux: `Kernel` — affected >=6.1.0 <6.1.79, >=6.2.0 <6.6.18, >=6.7.0 <6.7.6

## Details
In the Linux kernel, the following vulnerability has been resolved:

lan966x: Fix crash when adding interface under a lag

There is a crash when adding one of the lan966x interfaces under a lag
interface. The issue can be reproduced like this:
ip link add name bond0 type bond miimon 100 mode balance-xor
ip link set dev eth0 master bond0

The reason is because when adding a interface under the lag it would go
through all the ports and try to figure out which other ports are under
that lag interface. And the issue is that lan966x can have ports that are
NULL pointer as they are not probed. So then iterating over these ports
it would just crash as they are NULL pointers.
The fix consists in actually checking for NULL pointers before accessing
something from the ports. Like we do in other places.

## References
- https://git.kernel.org/stable/c/15faa1f67ab405d47789d4702f587ec7df7ef03e
- https://git.kernel.org/stable/c/2a492f01228b7d091dfe38974ef40dccf8f9f2f1
- https://git.kernel.org/stable/c/48fae67d837488c87379f0c9f27df7391718477c
- https://git.kernel.org/stable/c/b9357489c46c7a43999964628db8b47d3a1f8672
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2024/26xxx/CVE-2024-26723.json
- https://nvd.nist.gov/vuln/detail/CVE-2024-26723
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
