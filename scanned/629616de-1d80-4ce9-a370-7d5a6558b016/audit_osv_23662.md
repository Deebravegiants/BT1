# [M] tty: synclink_gt: Fix null-pointer-dereference in slgt_clean()

## Summary
Severity: Medium
Advisory: CVE-2022-49307
Ecosystem: Linux
CVSS: 5.5 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:N/I:N/A:H)
Published: 2025-02-26
Source: https://osv.dev/vulnerability/CVE-2022-49307
Type: osv

## Affected
- Linux: `Kernel` — affected >=2.6.16 <4.9.318, >=4.10.0 <4.14.283, >=4.15.0 <4.19.247, >=4.20.0 <5.4.198, >=5.5.0 <5.10.122, >=5.11.0 <5.15.47, >=5.16.0 <5.17.15, >=5.18.0 <5.18.4

## Details
In the Linux kernel, the following vulnerability has been resolved:

tty: synclink_gt: Fix null-pointer-dereference in slgt_clean()

When the driver fails at alloc_hdlcdev(), and then we remove the driver
module, we will get the following splat:

[   25.065966] general protection fault, probably for non-canonical address 0xdffffc0000000182: 0000 [#1] PREEMPT SMP KASAN PTI
[   25.066914] KASAN: null-ptr-deref in range [0x0000000000000c10-0x0000000000000c17]
[   25.069262] RIP: 0010:detach_hdlc_protocol+0x2a/0x3e0
[   25.077709] Call Trace:
[   25.077924]  <TASK>
[   25.078108]  unregister_hdlc_device+0x16/0x30
[   25.078481]  slgt_cleanup+0x157/0x9f0 [synclink_gt]

Fix this by checking whether the 'info->netdev' is a null pointer first.

## References
- https://git.kernel.org/stable/c/078212ad15dbd88840c82c97f12c93d83703c8fd
- https://git.kernel.org/stable/c/1ceb4ca9543a8a788febf6bc8dad2e605e172d5e
- https://git.kernel.org/stable/c/50c341f9a2adc4c32a8ad5a39eb99d9c4a419e0d
- https://git.kernel.org/stable/c/689ca31c542687709ba21ec2195c1fbce34fd029
- https://git.kernel.org/stable/c/8a95696bdc0e13f8980f05b54a3b9081963d1256
- https://git.kernel.org/stable/c/ba08cbc5b53e151d0acf1930fb526fc65b7f3e65
- https://git.kernel.org/stable/c/d68d5e68b7f64de7170f8e04dd9b995c36b2c71c
- https://git.kernel.org/stable/c/ddd67751ab86c6a65f95c35293c42f85a42ac05d
- https://git.kernel.org/stable/c/f6e07eb7ebec53ffe81fc2489589320fbe4a6b75
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2022/49xxx/CVE-2022-49307.json
- https://nvd.nist.gov/vuln/detail/CVE-2022-49307
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
