# [H] CVE-2022-3545

## Summary
Severity: High
Advisory: CVE-2022-3545
CVSS: 7.8 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H)
Published: 2022-10-17
Source: https://osv.dev/vulnerability/CVE-2022-3545
Type: osv

## Details
A vulnerability has been found in Linux Kernel and classified as critical. Affected by this vulnerability is the function area_cache_get of the file drivers/net/ethernet/netronome/nfp/nfpcore/nfp_cppcore.c of the component IPsec. The manipulation leads to use after free. It is recommended to apply a patch to fix this issue. The identifier VDB-211045 was assigned to this vulnerability.

## References
- https://lists.debian.org/debian-lts-announce/2023/03/msg00000.html
- https://lists.debian.org/debian-lts-announce/2023/05/msg00006.html
- https://security.netapp.com/advisory/ntap-20221223-0003/
- https://vuldb.com/?id.211045
- https://www.debian.org/security/2023/dsa-5324
- https://git.kernel.org/pub/scm/linux/kernel/git/klassert/ipsec-next.git/commit/?id=02e1a114fdb71e59ee6770294166c30d437bf86a
