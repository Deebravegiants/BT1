# [H] serial: sc16is7xx: fix TX fifo corruption

## Summary
Severity: High
Advisory: CVE-2024-44951
Ecosystem: Linux
CVSS: 7.8 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H)
Published: 2024-09-04
Source: https://osv.dev/vulnerability/CVE-2024-44951
Type: osv

## Affected
- Linux: `Kernel` — affected >=6.8.0 <6.10.5

## Details
In the Linux kernel, the following vulnerability has been resolved:

serial: sc16is7xx: fix TX fifo corruption

Sometimes, when a packet is received on channel A at almost the same time
as a packet is about to be transmitted on channel B, we observe with a
logic analyzer that the received packet on channel A is transmitted on
channel B. In other words, the Tx buffer data on channel B is corrupted
with data from channel A.

The problem appeared since commit 4409df5866b7 ("serial: sc16is7xx: change
EFR lock to operate on each channels"), which changed the EFR locking to
operate on each channel instead of chip-wise.

This commit has introduced a regression, because the EFR lock is used not
only to protect the EFR registers access, but also, in a very obscure and
undocumented way, to protect access to the data buffer, which is shared by
the Tx and Rx handlers, but also by each channel of the IC.

Fix this regression first by switching to kfifo_out_linear_ptr() in
sc16is7xx_handle_tx() to eliminate the need for a shared Rx/Tx buffer.

Secondly, replace the chip-wise Rx buffer with a separate Rx buffer for
each channel.

## References
- https://git.kernel.org/stable/c/09cfe05e9907f3276887a20e267cc40e202f4fdd
- https://git.kernel.org/stable/c/133f4c00b8b2bfcacead9b81e7e8edfceb4b06c4
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2024/44xxx/CVE-2024-44951.json
- https://nvd.nist.gov/vuln/detail/CVE-2024-44951
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
