# [C] dlm: validate length in dlm_search_rsb_tree

## Summary
Severity: Critical
Advisory: CVE-2026-43125
Ecosystem: Linux
CVSS: 9.8 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H)
Published: 2026-05-06
Source: https://osv.dev/vulnerability/CVE-2026-43125
Type: osv

## Affected
- Linux: `Kernel` — affected >=3.4.0 <6.12.75, >=6.13.0 <6.18.16, >=6.19.0 <6.19.6

## Details
In the Linux kernel, the following vulnerability has been resolved:

dlm: validate length in dlm_search_rsb_tree

The len parameter in dlm_dump_rsb_name() is not validated and comes
from network messages. When it exceeds DLM_RESNAME_MAXLEN, it can
cause out-of-bounds write in dlm_search_rsb_tree().

Add length validation to prevent potential buffer overflow.

## References
- https://git.kernel.org/stable/c/080e5563f878c64e697b89e7439d730d0daad882
- https://git.kernel.org/stable/c/082083c9fbd99422a0370fe2102144a231c9f5d6
- https://git.kernel.org/stable/c/5f053a2e7209d326cbbc07738fa6d6893d307438
- https://git.kernel.org/stable/c/67288113c5e6cf9e659b4065c0ed6f16100e0c71
- https://security.access.redhat.com/data/csaf/v2/vex/2026/cve-2026-43125.json
- https://access.redhat.com/errata/RHSA-2026:25120
- https://access.redhat.com/errata/RHSA-2026:25121
- https://access.redhat.com/errata/RHSA-2026:25217
- https://access.redhat.com/errata/RHSA-2026:33899
- https://access.redhat.com/errata/RHSA-2026:33900
- https://access.redhat.com/errata/RHSA-2026:34094
- https://access.redhat.com/errata/RHSA-2026:34095
- https://access.redhat.com/errata/RHSA-2026:35844
- https://access.redhat.com/errata/RHSA-2026:35863
- https://access.redhat.com/errata/RHSA-2026:36767
- https://access.redhat.com/errata/RHSA-2026:41236
- https://access.redhat.com/errata/RHSA-2026:55761
- https://access.redhat.com/errata/RHSA-2026:55762
- https://access.redhat.com/errata/RHSA-2026:55763
- https://access.redhat.com/errata/RHSA-2026:55837
