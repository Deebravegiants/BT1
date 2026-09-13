# [H] CVE-2022-3635

## Summary
Severity: High
Advisory: CVE-2022-3635
CVSS: 7.0 (CVSS:3.1/AV:L/AC:H/PR:L/UI:N/S:U/C:H/I:H/A:H)
Published: 2022-10-21
Source: https://osv.dev/vulnerability/CVE-2022-3635
Type: osv

## Details
A vulnerability, which was classified as critical, has been found in Linux Kernel. Affected by this issue is the function tst_timer of the file drivers/atm/idt77252.c of the component IPsec. The manipulation leads to use after free. It is recommended to apply a patch to fix this issue. VDB-211934 is the identifier assigned to this vulnerability.

## References
- https://lists.debian.org/debian-lts-announce/2022/11/msg00001.html
- https://vuldb.com/?id.211934
- https://git.kernel.org/pub/scm/linux/kernel/git/klassert/ipsec-next.git/commit/?id=3f4093e2bf4673f218c0bf17d8362337c400e77b
