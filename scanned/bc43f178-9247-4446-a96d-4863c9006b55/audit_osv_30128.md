# [H] sfc: Don't invoke xdp_do_flush() from netpoll.

## Summary
Severity: High
Advisory: CVE-2024-50094
Ecosystem: Linux
CVSS: 7.5 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:H)
Published: 2024-11-05
Source: https://osv.dev/vulnerability/CVE-2024-50094
Type: osv

## Affected
- Linux: `Kernel` — affected >=6.11.0 <6.11.4

## Details
In the Linux kernel, the following vulnerability has been resolved:

sfc: Don't invoke xdp_do_flush() from netpoll.

Yury reported a crash in the sfc driver originated from
netpoll_send_udp(). The netconsole sends a message and then netpoll
invokes the driver's NAPI function with a budget of zero. It is
dedicated to allow driver to free TX resources, that it may have used
while sending the packet.

In the netpoll case the driver invokes xdp_do_flush() unconditionally,
leading to crash because bpf_net_context was never assigned.

Invoke xdp_do_flush() only if budget is not zero.

## References
- https://git.kernel.org/stable/c/55e802468e1d38dec8e25a2fdb6078d45b647e8c
- https://git.kernel.org/stable/c/65d4fc76d75c136744e67754d20feda609e7b793
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2024/50xxx/CVE-2024-50094.json
- https://nvd.nist.gov/vuln/detail/CVE-2024-50094
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
