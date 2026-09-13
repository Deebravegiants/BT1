# [H] media: dvbdev: prevent the risk of out of memory access

## Summary
Severity: High
Advisory: CVE-2024-53063
Ecosystem: Linux
CVSS: 7.8 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H)
Published: 2024-11-19
Source: https://osv.dev/vulnerability/CVE-2024-53063
Type: osv

## Affected
- Linux: `Kernel` — affected >=2.6.29 <4.19.324, >=4.20.0 <5.4.286, >=5.5.0 <5.10.230, >=5.11.0 <5.15.172, >=5.16.0 <6.1.117, >=6.2.0 <6.6.61, >=6.7.0 <6.11.8

## Details
In the Linux kernel, the following vulnerability has been resolved:

media: dvbdev: prevent the risk of out of memory access

The dvbdev contains a static variable used to store dvb minors.

The behavior of it depends if CONFIG_DVB_DYNAMIC_MINORS is set
or not. When not set, dvb_register_device() won't check for
boundaries, as it will rely that a previous call to
dvb_register_adapter() would already be enforcing it.

On a similar way, dvb_device_open() uses the assumption
that the register functions already did the needed checks.

This can be fragile if some device ends using different
calls. This also generate warnings on static check analysers
like Coverity.

So, add explicit guards to prevent potential risk of OOM issues.

## References
- https://git.kernel.org/stable/c/1e461672616b726f29261ee81bb991528818537c
- https://git.kernel.org/stable/c/3b88675e18b6517043a6f734eaa8ea6eb3bfa140
- https://git.kernel.org/stable/c/5f76f7df14861e3a560898fa41979ec92424b58f
- https://git.kernel.org/stable/c/972e63e895abbe8aa1ccbdbb4e6362abda7cd457
- https://git.kernel.org/stable/c/9c17085fabbde2041c893d29599800f2d4992b23
- https://git.kernel.org/stable/c/a4a17210c03ade1c8d9a9f193a105654b7a05c11
- https://git.kernel.org/stable/c/b751a96025275c17f04083cbfe856822f1658946
- https://git.kernel.org/stable/c/fedfde9deb83ac8d2f3d5f36f111023df34b1684
- https://lists.debian.org/debian-lts-announce/2025/01/msg00001.html
- https://lists.debian.org/debian-lts-announce/2025/03/msg00002.html
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2024/53xxx/CVE-2024-53063.json
- https://nvd.nist.gov/vuln/detail/CVE-2024-53063
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
