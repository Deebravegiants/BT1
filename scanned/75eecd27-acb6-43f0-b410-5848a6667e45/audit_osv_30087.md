# [H] net: Fix an unsafe loop on the list

## Summary
Severity: High
Advisory: CVE-2024-50024
Ecosystem: Linux
CVSS: 7.3 (CVSS:3.1/AV:L/AC:L/PR:L/UI:R/S:U/C:H/I:H/A:H)
Published: 2024-10-21
Source: https://osv.dev/vulnerability/CVE-2024-50024
Type: osv

## Affected
- Linux: `Kernel` — affected >=2.6.32 <4.19.323, >=4.20.0 <5.4.285, >=5.5.0 <5.10.227, >=5.11.0 <5.15.168, >=5.16.0 <6.1.113, >=6.2.0 <6.6.57, >=6.7.0 <6.11.4

## Details
In the Linux kernel, the following vulnerability has been resolved:

net: Fix an unsafe loop on the list

The kernel may crash when deleting a genetlink family if there are still
listeners for that family:

Oops: Kernel access of bad area, sig: 11 [#1]
  ...
  NIP [c000000000c080bc] netlink_update_socket_mc+0x3c/0xc0
  LR [c000000000c0f764] __netlink_clear_multicast_users+0x74/0xc0
  Call Trace:
__netlink_clear_multicast_users+0x74/0xc0
genl_unregister_family+0xd4/0x2d0

Change the unsafe loop on the list to a safe one, because inside the
loop there is an element removal from this list.

## References
- https://git.kernel.org/stable/c/1cdec792b2450105b1314c5123a9a0452cb2c2f0
- https://git.kernel.org/stable/c/1dae9f1187189bc09ff6d25ca97ead711f7e26f9
- https://git.kernel.org/stable/c/3be342e0332a7c83eb26fbb22bf156fdca467a5d
- https://git.kernel.org/stable/c/464801a0f6ccb52b21faa33bac6014fd74cc5e10
- https://git.kernel.org/stable/c/49f9b726bf2bf3dd2caf0d27cadf4bc1ccf7a7dd
- https://git.kernel.org/stable/c/5f03a7f601f33cda1f710611625235dc86fd8a9e
- https://git.kernel.org/stable/c/68ad5da6ca630a276f0a5c924179e57724d00013
- https://git.kernel.org/stable/c/8e0766fcf37ad8eed289dd3853628dd9b01b58b0
- https://lists.debian.org/debian-lts-announce/2025/01/msg00001.html
- https://lists.debian.org/debian-lts-announce/2025/03/msg00002.html
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2024/50xxx/CVE-2024-50024.json
- https://nvd.nist.gov/vuln/detail/CVE-2024-50024
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
