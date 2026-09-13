# [H] Bluetooth: bnep: Fix UAF read of dev->name

## Summary
Severity: High
Advisory: CVE-2026-64178
Ecosystem: Linux
CVSS: 8.8 (CVSS:3.1/AV:A/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H)
Published: 2026-07-19
Source: https://osv.dev/vulnerability/CVE-2026-64178
Type: osv

## Affected
- Linux: `Kernel` — affected >=2.6.12 <5.10.258, >=5.11.0 <5.15.209, >=5.16.0 <6.1.175, >=6.2.0 <6.6.142, >=6.7.0 <6.12.92, >=6.13.0 <6.18.34, >=6.19.0 <7.0.11

## Details
In the Linux kernel, the following vulnerability has been resolved:

Bluetooth: bnep: Fix UAF read of dev->name

bnep_add_connection() needs to keep holding the bnep_session_sem while
reading dev->name (just like bnep_get_connlist() does); otherwise the
bnep_session() thread can concurrently free the net_device, which can for
example be triggered by a concurrent bnep_del_connection().

(This UAF is fairly uninteresting from a security perspective;
calling bnep_add_connection() requires passing a capable(CAP_NET_ADMIN)
check. It also requires completely tearing down a netdev during a fairly
tight race window.)

## References
- https://git.kernel.org/stable/c/4907596f25b1720fa948371ac5f6c1f8da10a5bc
- https://git.kernel.org/stable/c/5506aec795135cdd4cbf4e845929155663b25055
- https://git.kernel.org/stable/c/59e932ded949fa6f0340bf7c6d7818f962fa4fd2
- https://git.kernel.org/stable/c/915a92182e2cda9cd7d2479020a44c6eda986f7c
- https://git.kernel.org/stable/c/a75bbcb10cb21acc169b785e9804f57d97873a9c
- https://git.kernel.org/stable/c/b21805258d7e926adfd455fc820a447b90da3b82
- https://git.kernel.org/stable/c/e7578529b97e5d4e439cf8f3e637c2303015338f
- https://git.kernel.org/stable/c/fe69f634b076ae3ca81c5a5b845d9bba527036f7
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/64xxx/CVE-2026-64178.json
- https://nvd.nist.gov/vuln/detail/CVE-2026-64178
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
