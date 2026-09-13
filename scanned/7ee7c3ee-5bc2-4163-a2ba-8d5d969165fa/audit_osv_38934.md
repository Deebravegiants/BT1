# [H] fs/smb/client: fix out-of-bounds read in cifs_sanitize_prepath

## Summary
Severity: High
Advisory: CVE-2026-43112
Ecosystem: Linux
CVSS: 8.8 (CVSS:3.1/AV:N/AC:L/PR:N/UI:R/S:U/C:H/I:H/A:H)
Published: 2026-05-06
Source: https://osv.dev/vulnerability/CVE-2026-43112
Type: osv

## Affected
- Linux: `Kernel` — affected >=0 <5.15.209, >=5.16.0 <6.6.136, >=6.2.0 <6.12.83, >=6.7.0 <6.18.24, >=6.13.0 <6.19.14

## Details
In the Linux kernel, the following vulnerability has been resolved:

fs/smb/client: fix out-of-bounds read in cifs_sanitize_prepath

When cifs_sanitize_prepath is called with an empty string or a string
containing only delimiters (e.g., "/"), the current logic attempts to
check *(cursor2 - 1) before cursor2 has advanced. This results in an
out-of-bounds read.

This patch adds an early exit check after stripping prepended
delimiters. If no path content remains, the function returns NULL.

The bug was identified via manual audit and verified using a
standalone test case compiled with AddressSanitizer, which
triggered a SEGV on affected inputs.

## References
- https://git.kernel.org/stable/c/2d29214448ec0f4e7e18bb1c14dd4a6c07f1c439
- https://git.kernel.org/stable/c/49b1ce6d7cfb6c5a49f68bf5ccfcfb6ba14e63c3
- https://git.kernel.org/stable/c/5d4fe469fe7dbff7d874c196bb680a82f2625d95
- https://git.kernel.org/stable/c/78ec5bf2f589ec7fd8f169394bfeca541b077317
- https://git.kernel.org/stable/c/86f9c23e0814cfdffda9eedf0c591c51ba209010
- https://git.kernel.org/stable/c/a2ba20c17de8eb028f96b1d85f119d3d25655bd9
- https://git.kernel.org/stable/c/fbced33599653471b4581dfe1abc7b467031f126
- https://security.access.redhat.com/data/csaf/v2/vex/2026/cve-2026-43112.json
- https://access.redhat.com/errata/RHSA-2026:34911
- https://access.redhat.com/errata/RHSA-2026:36018
- https://access.redhat.com/errata/RHSA-2026:36365
- https://access.redhat.com/errata/RHSA-2026:36366
- https://access.redhat.com/errata/RHSA-2026:40764
- https://access.redhat.com/errata/RHSA-2026:52649
- https://access.redhat.com/errata/RHSA-2026:52764
- https://access.redhat.com/errata/RHSA-2026:53989
- https://access.redhat.com/errata/RHSA-2026:53990
- https://access.redhat.com/errata/RHSA-2026:56573
- https://access.redhat.com/errata/RHSA-2026:57402
- https://access.redhat.com/errata/RHSA-2026:57457
