# [H] net: qrtr: restrict socket creation to the initial network namespace

## Summary
Severity: High
Advisory: CVE-2026-68294
Ecosystem: Linux
CVSS: 8.8 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:C/C:H/I:H/A:H)
Published: 2026-08-10
Source: https://osv.dev/vulnerability/CVE-2026-68294
Type: osv

## Affected
- Linux: `Kernel` — affected >=4.7.0 <5.10.265, >=5.11.0 <5.15.216, >=5.16.0 <6.1.183, >=6.2.0 <6.6.148, >=6.7.0 <6.12.101, >=6.13.0 <6.18.42, >=6.19.0 <7.1.6

## Details
In the Linux kernel, the following vulnerability has been resolved:

net: qrtr: restrict socket creation to the initial network namespace

QRTR keeps its entire port and node state in module-global variables
that are not partitioned per network namespace: qrtr_local_nid is a
single global node id (always 1) and qrtr_ports is a single global
xarray. qrtr_port_lookup() and qrtr_local_enqueue() operate on that
global state with no network-namespace check, and qrtr_create() places
no restriction on the namespace a socket is created in.

As a result an unprivileged process that creates an AF_QIPCRTR socket
in a separate network namespace, e.g. via
unshare(CLONE_NEWUSER | CLONE_NEWNET), can send QRTR datagrams -
including control-plane messages such as QRTR_TYPE_NEW_SERVER - to QRTR
sockets owned by another namespace, and vice versa. The receiving
socket sees such a message as coming from node id 1, indistinguishable
from a legitimate local client, breaking the isolation that network
namespaces are expected to provide.

QRTR is a transport to global hardware endpoints (the modem and other
remote processors) and has no per-namespace semantics; its in-kernel
name service already creates its socket in init_net only. Confine the
socket family to the initial network namespace, as other
non-namespace-aware socket families do (see llc_ui_create() and the
ieee802154 socket code).

## References
- https://git.kernel.org/stable/c/2d22b94a154ccb9755dddfff802fe3e2b1adbab5
- https://git.kernel.org/stable/c/3b536db8fb32da9e9c62f2bb45e2e319331f0426
- https://git.kernel.org/stable/c/4b95e1f0d6e6342c427cb341ee18a894b146b789
- https://git.kernel.org/stable/c/659b9b4f194bb56b9903cc95e786ef1d438baa7d
- https://git.kernel.org/stable/c/7814f6a3415cad38aa8d6dfc573df778260d66aa
- https://git.kernel.org/stable/c/8150c48fb978e01689f94ed80148f8a7499ae571
- https://git.kernel.org/stable/c/8d351fe0654a20c9f95a61b05d24ebe6d4be3fbb
- https://git.kernel.org/stable/c/f488116df769bdaf89c93371350e49e12133e70f
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/68xxx/CVE-2026-68294.json
- https://nvd.nist.gov/vuln/detail/CVE-2026-68294
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
