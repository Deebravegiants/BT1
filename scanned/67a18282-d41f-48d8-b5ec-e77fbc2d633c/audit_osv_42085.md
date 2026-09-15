# [H] usb: typec: tcpci_rt1711h: unregister TCPCI port with devres

## Summary
Severity: High
Advisory: CVE-2026-64463
Ecosystem: Linux
CVSS: 7.8 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H)
Published: 2026-07-25
Source: https://osv.dev/vulnerability/CVE-2026-64463
Type: osv

## Affected
- Linux: `Kernel` — affected >=5.8.0 <6.6.145, >=6.7.0 <6.12.96, >=6.13.0 <6.18.39, >=6.19.0 <7.1.4

## Details
In the Linux kernel, the following vulnerability has been resolved:

usb: typec: tcpci_rt1711h: unregister TCPCI port with devres

rt1711h_probe() registers the TCPCI port before requesting the interrupt
and enabling alert interrupts. If either of those later steps fails, the
probe function returns without unregistering the TCPCI port. The explicit
unregister currently only happens from the remove callback.

Register a devres action immediately after tcpci_register_port() succeeds,
so tcpci_unregister_port() runs on later probe failures and on driver
detach. Drop the remove callback to avoid unregistering the same port
twice.

This issue was identified during our ongoing static-analysis research while
reviewing kernel code.

## References
- https://git.kernel.org/stable/c/569f18a83eed0b0be4615f0c7bed40fb5c50e2e6
- https://git.kernel.org/stable/c/94b1abf1af94aa5a355e9f03675e07bccfc41c4b
- https://git.kernel.org/stable/c/ce2e36e8759dfbfe546723810c306f42f484866d
- https://git.kernel.org/stable/c/e5406c8fb71cd2f89a46300a746f6e7972e621e8
- https://git.kernel.org/stable/c/e8da46d99d3710106e7c44db14566bf9b57386b5
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/64xxx/CVE-2026-64463.json
- https://nvd.nist.gov/vuln/detail/CVE-2026-64463
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
