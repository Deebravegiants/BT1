# [H] netfilter: nf_tables: make nft_object rhltable per table

## Summary
Severity: High
Advisory: CVE-2026-74565
Ecosystem: Linux
CVSS: 7.8 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H)
Published: 2026-08-15
Source: https://osv.dev/vulnerability/CVE-2026-74565
Type: osv

## Affected
- Linux: `Kernel` — affected >=5.1.0 <6.12.103, >=6.13.0 <6.18.44, >=6.19.0 <7.1.8

## Details
In the Linux kernel, the following vulnerability has been resolved:

netfilter: nf_tables: make nft_object rhltable per table

The nft_object rhltable is global, this allows for accessing objects
that are being dismangled from lookup path by other existing netns.
Given the nft_obj_destroy() releases the object inmediately, this might
lead to use-after-free of these objects that are being released.
Make the existing rhltable per table to address this issue to deal with
with the nft_rcv_nl_event() path too.

Update nft_obj_lookup() to take the table as non-const, otherwise,
compiler complains when passing the objname_ht to rhltable_lookup().

## References
- https://git.kernel.org/stable/c/1948e4f85b855618b5b9a27265f98d816f4cb7cb
- https://git.kernel.org/stable/c/63ba12b664a2cd3220ed43e22c717715f4cc2ae8
- https://git.kernel.org/stable/c/7d4789b58761d9d48d9b5f5e7e0a510c3bbfb3af
- https://git.kernel.org/stable/c/f4f699790590bd0896c48a71e9232a65198f92f0
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/74xxx/CVE-2026-74565.json
- https://nvd.nist.gov/vuln/detail/CVE-2026-74565
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
