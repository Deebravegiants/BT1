# [C] netfilter: flowtable: avoid num_encaps underflow on bridge VLAN untag

## Summary
Severity: Critical
Advisory: CVE-2026-80634
Ecosystem: Linux
CVSS: 9.8 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H)
Published: 2026-08-28
Source: https://osv.dev/vulnerability/CVE-2026-80634
Type: osv

## Affected
- Linux: `Kernel` — affected >=5.13.0 <7.1.5

## Details
In the Linux kernel, the following vulnerability has been resolved:

netfilter: flowtable: avoid num_encaps underflow on bridge VLAN untag

The DEV_PATH_BR_VLAN_UNTAG case post-decrements info->num_encaps
inside WARN_ON_ONCE(). num_encaps is u8, so if it's already 0 the
decrement still happens and wraps it to 255. The break only leaves
the inner switch -- a later path entry can set info->indev back to
a real device, and we end up returning with num_encaps == 255.

nft_dev_forward_path() then walks info.encap[] (size 2) up to
num_encaps, which means an OOB stack read and a bogus count copied
into the route descriptor.

Should only happen on a malformed bridge path stack, hence the WARN,
but worth handling sanely. Move the decrement out of the WARN.

[ While at this, remove the WARN_ON_ONCE since this can only happen
  with a buggy bridge path stack --pablo ].

## References
- https://git.kernel.org/stable/c/2f55fa28011c97d6495d5787808db10a8c2d690d
- https://git.kernel.org/stable/c/e052f920773b73be49eb4d8702a9f85de7464363
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/80xxx/CVE-2026-80634.json
- https://nvd.nist.gov/vuln/detail/CVE-2026-80634
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
