# [H] Bluetooth: SCO: Fix use-after-free in sco_recv_frame() due to missing sock_hold

## Summary
Severity: High
Advisory: CVE-2026-31408
Ecosystem: Linux
CVSS: 8.8 (CVSS:3.1/AV:A/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H)
Published: 2026-04-06
Source: https://osv.dev/vulnerability/CVE-2026-31408
Type: osv

## Affected
- Linux: `Kernel` — affected >=2.6.12 <5.10.265, >=5.11.0 <5.15.203, >=5.16.0 <6.1.168, >=6.2.0 <6.6.131, >=6.7.0 <6.12.80, >=6.13.0 <6.18.21, >=6.19.0 <6.19.11

## Details
In the Linux kernel, the following vulnerability has been resolved:

Bluetooth: SCO: Fix use-after-free in sco_recv_frame() due to missing sock_hold

sco_recv_frame() reads conn->sk under sco_conn_lock() but immediately
releases the lock without holding a reference to the socket. A concurrent
close() can free the socket between the lock release and the subsequent
sk->sk_state access, resulting in a use-after-free.

Other functions in the same file (sco_sock_timeout(), sco_conn_del())
correctly use sco_sock_hold() to safely hold a reference under the lock.

Fix by using sco_sock_hold() to take a reference before releasing the
lock, and adding sock_put() on all exit paths.

## References
- https://git.kernel.org/stable/c/108b81514d8f2535eb16651495cefb2250528db3
- https://git.kernel.org/stable/c/37e18bc8c9a70d77bd099e2273f328b3bc7f6d0d
- https://git.kernel.org/stable/c/45aaca995e4a7a05b272a58e7ab2fff4f611b8f1
- https://git.kernel.org/stable/c/598dbba9919c5e36c54fe1709b557d64120cb94b
- https://git.kernel.org/stable/c/7197462e90b8ce15caa1ae15d4bc2bb8cd21b11e
- https://git.kernel.org/stable/c/b0a7da0e3f7442545f071499beb36374714bb9de
- https://git.kernel.org/stable/c/d57384e27d1ebf0047e3f00a6e1181b8be9857a2
- https://git.kernel.org/stable/c/e76e8f0581ef555eacc11dbb095e602fb30a5361
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/31xxx/CVE-2026-31408.json
- https://nvd.nist.gov/vuln/detail/CVE-2026-31408
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
