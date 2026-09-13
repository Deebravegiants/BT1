# [M] CVE-2022-3567

## Summary
Severity: Medium
Advisory: CVE-2022-3567
CVSS: 6.4 (CVSS:3.1/AV:A/AC:H/PR:N/UI:N/S:U/C:L/I:L/A:H)
Published: 2022-10-17
Source: https://osv.dev/vulnerability/CVE-2022-3567
Type: osv

## Details
A vulnerability has been found in Linux Kernel and classified as problematic. This vulnerability affects the function inet6_stream_ops/inet6_dgram_ops of the component IPv6 Handler. The manipulation leads to race condition. It is recommended to apply a patch to fix this issue. VDB-211090 is the identifier assigned to this vulnerability.

## References
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git/commit/?id=364f997b5cfe1db0d63a390fe7c801fa2b3115f6
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git/commit/?id=364f997b5cfe1db0d63a390fe7c801fa2b3115f6
- https://vuldb.com/?id.211090
