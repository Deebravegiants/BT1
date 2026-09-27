# [C] tunnels: fix out of bounds access when building IPv6 PMTU error

## Summary
Severity: Critical
Advisory: CVE-2024-26665
Ecosystem: Linux
CVSS: 9.1 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:N/A:H)
Published: 2024-04-02
Source: https://osv.dev/vulnerability/CVE-2024-26665
Type: osv

## Affected
- Linux: `Kernel` — affected >=5.9.0 <5.10.210, >=5.11.0 <5.15.149, >=5.16.0 <6.1.78, >=6.2.0 <6.6.17, >=6.7.0 <6.7.5

## Details
In the Linux kernel, the following vulnerability has been resolved:

tunnels: fix out of bounds access when building IPv6 PMTU error

If the ICMPv6 error is built from a non-linear skb we get the following
splat,

  BUG: KASAN: slab-out-of-bounds in do_csum+0x220/0x240
  Read of size 4 at addr ffff88811d402c80 by task netperf/820
  CPU: 0 PID: 820 Comm: netperf Not tainted 6.8.0-rc1+ #543
  ...
   kasan_report+0xd8/0x110
   do_csum+0x220/0x240
   csum_partial+0xc/0x20
   skb_tunnel_check_pmtu+0xeb9/0x3280
   vxlan_xmit_one+0x14c2/0x4080
   vxlan_xmit+0xf61/0x5c00
   dev_hard_start_xmit+0xfb/0x510
   __dev_queue_xmit+0x7cd/0x32a0
   br_dev_queue_push_xmit+0x39d/0x6a0

Use skb_checksum instead of csum_partial who cannot deal with non-linear
SKBs.

## References
- https://git.kernel.org/stable/c/510c869ffa4068c5f19ff4df51d1e2f3a30aaac1
- https://git.kernel.org/stable/c/7dc9feb8b1705cf00de20563b6bc4831f4c99dab
- https://git.kernel.org/stable/c/d75abeec401f8c86b470e7028a13fcdc87e5dd06
- https://git.kernel.org/stable/c/d964dd1bc1452594b4207d9229c157d9386e5d8a
- https://git.kernel.org/stable/c/e37cde7a5716466ff2a76f7f27f0a29b05b9a732
- https://git.kernel.org/stable/c/e77bf828f1ca1c47fcff58bdc26b60a9d3dfbe1d
- https://lists.debian.org/debian-lts-announce/2024/06/msg00017.html
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2024/26xxx/CVE-2024-26665.json
- https://nvd.nist.gov/vuln/detail/CVE-2024-26665
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
