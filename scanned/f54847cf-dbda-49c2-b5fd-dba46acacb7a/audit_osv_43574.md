# [C] vxlan: Fix potential null-ptr-deref in vxlan_gro_prepare_receive().

## Summary
Severity: Critical
Advisory: CVE-2026-74406
Ecosystem: Linux
CVSS: 9.8 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H)
Published: 2026-08-15
Source: https://osv.dev/vulnerability/CVE-2026-74406
Type: osv

## Affected
- Linux: `Kernel` — affected >=4.7.0 <6.1.178, >=6.2.0 <6.6.145, >=6.7.0 <6.12.97, >=6.13.0 <6.18.40, >=6.19.0 <7.1.5

## Details
In the Linux kernel, the following vulnerability has been resolved:

vxlan: Fix potential null-ptr-deref in vxlan_gro_prepare_receive().

udp_tunnel_sock_release() could set sk->sk_user_data to NULL
while vxlan_gro_prepare_receive() is running.

Let's check if rcu_dereference_sk_user_data() is NULL after
skb_gro_remcsum_init().

## References
- https://git.kernel.org/stable/c/08f40c0d23c67c3aa4224c3311e134999c721fb4
- https://git.kernel.org/stable/c/30a45c0bffdd62350261e2f2689fdba426a33578
- https://git.kernel.org/stable/c/4a8cde6f7281ea2c4c290f9ad9923b3631defceb
- https://git.kernel.org/stable/c/9c58c729d32e7cea5772cc44929c6cd61e5a31cd
- https://git.kernel.org/stable/c/ef44dac2a37f86eeae6b88ed10a6d60b35387dfd
- https://git.kernel.org/stable/c/f79c80f173fda9545b220c1f094b65fc06c252d0
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/74xxx/CVE-2026-74406.json
- https://nvd.nist.gov/vuln/detail/CVE-2026-74406
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
