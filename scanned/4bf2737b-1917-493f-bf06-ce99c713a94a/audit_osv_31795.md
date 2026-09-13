# [H] vrf: use RCU protection in l3mdev_l3_out()

## Summary
Severity: High
Advisory: CVE-2025-21791
Ecosystem: Linux
CVSS: 7.8 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H)
Published: 2025-02-27
Source: https://osv.dev/vulnerability/CVE-2025-21791
Type: osv

## Affected
- Linux: `Kernel` — affected >=4.9.0 <5.4.291, >=5.5.0 <5.10.235, >=5.11.0 <5.15.179, >=5.16.0 <6.1.129, >=6.2.0 <6.6.79, >=6.7.0 <6.12.16, >=6.13.0 <6.13.4

## Details
In the Linux kernel, the following vulnerability has been resolved:

vrf: use RCU protection in l3mdev_l3_out()

l3mdev_l3_out() can be called without RCU being held:

raw_sendmsg()
 ip_push_pending_frames()
  ip_send_skb()
   ip_local_out()
    __ip_local_out()
     l3mdev_ip_out()

Add rcu_read_lock() / rcu_read_unlock() pair to avoid
a potential UAF.

## References
- https://git.kernel.org/stable/c/022cac1c693add610ae76ede03adf4d9d5a2cf21
- https://git.kernel.org/stable/c/20a3489b396764cc9376e32a9172bee26a89dc3b
- https://git.kernel.org/stable/c/5bb4228c32261d06e4fbece37ec3828bcc005b6b
- https://git.kernel.org/stable/c/6ccaa5797f5362a2aad6baa6ddaf4715ac2dd51e
- https://git.kernel.org/stable/c/6d0ce46a93135d96b7fa075a94a88fe0da8e8773
- https://git.kernel.org/stable/c/7b81425b517accefd46bee854d94954f5c57e019
- https://git.kernel.org/stable/c/c40cb5c03e37552d6eff963187109e2c3f78ef6f
- https://git.kernel.org/stable/c/c7574740be8ce68a57d0aece24987b9be2114c3c
- https://lists.debian.org/debian-lts-announce/2025/03/msg00028.html
- https://lists.debian.org/debian-lts-announce/2025/05/msg00030.html
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2025/21xxx/CVE-2025-21791.json
- https://nvd.nist.gov/vuln/detail/CVE-2025-21791
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
