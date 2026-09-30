# [M] Bluetooth: rfcomm: Fix null-ptr-deref in rfcomm_check_security

## Summary
Severity: Medium
Advisory: CVE-2024-26903
Ecosystem: Linux
CVSS: 5.5 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:N/I:N/A:H)
Published: 2024-04-17
Source: https://osv.dev/vulnerability/CVE-2024-26903
Type: osv

## Affected
- Linux: `Kernel` — affected >=2.6.12 <4.19.311, >=4.20.0 <5.4.273, >=5.5.0 <5.10.214, >=5.11.0 <5.15.153, >=5.16.0 <6.1.83, >=6.2.0 <6.6.23, >=6.7.0 <6.7.11

## Details
In the Linux kernel, the following vulnerability has been resolved:

Bluetooth: rfcomm: Fix null-ptr-deref in rfcomm_check_security

During our fuzz testing of the connection and disconnection process at the
RFCOMM layer, we discovered this bug. By comparing the packets from a
normal connection and disconnection process with the testcase that
triggered a KASAN report. We analyzed the cause of this bug as follows:

1. In the packets captured during a normal connection, the host sends a
`Read Encryption Key Size` type of `HCI_CMD` packet
(Command Opcode: 0x1408) to the controller to inquire the length of
encryption key.After receiving this packet, the controller immediately
replies with a Command Completepacket (Event Code: 0x0e) to return the
Encryption Key Size.

2. In our fuzz test case, the timing of the controller's response to this
packet was delayed to an unexpected point: after the RFCOMM and L2CAP
layers had disconnected but before the HCI layer had disconnected.

3. After receiving the Encryption Key Size Response at the time described
in point 2, the host still called the rfcomm_check_security function.
However, by this time `struct l2cap_conn *conn = l2cap_pi(sk)->chan->conn;`
had already been released, and when the function executed
`return hci_conn_security(conn->hcon, d->sec_level, auth_type, d->out);`,
specifically when accessing `conn->hcon`, a null-ptr-deref error occurred.

To fix this bug, check if `sk->sk_state` is BT_CLOSED before calling
rfcomm_recv_frame in rfcomm_process_rx.

## References
- https://cert-portal.siemens.com/productcert/html/ssa-265688.html
- https://git.kernel.org/stable/c/2535b848fa0f42ddff3e5255cf5e742c9b77bb26
- https://git.kernel.org/stable/c/369f419c097e82407dd429a202cde9a73d3ae29b
- https://git.kernel.org/stable/c/3ead59bafad05f2967ae2438c0528d53244cfde5
- https://git.kernel.org/stable/c/567c0411dc3b424fc7bd1e6109726d7ba32d4f73
- https://git.kernel.org/stable/c/5f369efd9d963c1f711a06c9b8baf9f5ce616d85
- https://git.kernel.org/stable/c/5f9fe302dd3a9bbc50f4888464c1773f45166bfd
- https://git.kernel.org/stable/c/81d7d920a22fd58ef9aedb1bd0a68ee32bd23e96
- https://git.kernel.org/stable/c/8d1753973f598531baaa2c1033cf7f7b5bb004b0
- https://lists.debian.org/debian-lts-announce/2024/06/msg00017.html
- https://lists.debian.org/debian-lts-announce/2024/06/msg00020.html
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2024/26xxx/CVE-2024-26903.json
- https://nvd.nist.gov/vuln/detail/CVE-2024-26903
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
