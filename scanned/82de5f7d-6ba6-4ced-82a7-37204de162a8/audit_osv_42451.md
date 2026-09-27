# [C] sctp: close UDP tunnel sockets during netns teardown

## Summary
Severity: Critical
Advisory: CVE-2026-68161
Ecosystem: Linux
CVSS: 9.8 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H)
Published: 2026-08-10
Source: https://osv.dev/vulnerability/CVE-2026-68161
Type: osv

## Affected
- Linux: `Kernel` — affected >=5.11.0 <6.6.151, >=6.7.0 <6.12.101, >=6.13.0 <6.18.42, >=6.19.0 <7.1.6

## Details
In the Linux kernel, the following vulnerability has been resolved:

sctp: close UDP tunnel sockets during netns teardown

proc_sctp_do_udp_port() starts per-net SCTP UDP tunneling sockets when
net.sctp.udp_port is set, and stops/restarts them when the sysctl value
changes. The netns exit path does not stop these sockets, so a namespace
can be torn down while its SCTP UDP tunnel sockets are still installed.

Close the UDP tunnel sockets from sctp_ctrlsock_exit() after unregistering
the per-net sysctl table. This prevents new sysctl writes from racing in
while the sockets are being released, and closes the sockets before the
control socket is destroyed.

## References
- https://git.kernel.org/stable/c/37ff9794be48d0caa37687e04d09675f9c849121
- https://git.kernel.org/stable/c/3bf0e349cbb4f975f35eb22753acc346b89c66a0
- https://git.kernel.org/stable/c/8ff78591d309c50a4fdab683b68dd8d512a270dd
- https://git.kernel.org/stable/c/c6eb2d615210b80339548ab07c0230edaab9a6c7
- https://git.kernel.org/stable/c/ffb2bd7ade36ec4da32c46a6eddbf4515316d08c
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/68xxx/CVE-2026-68161.json
- https://nvd.nist.gov/vuln/detail/CVE-2026-68161
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
