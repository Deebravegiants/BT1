# [H] CVE-2022-3565

## Summary
Severity: High
Advisory: CVE-2022-3565
CVSS: 7.8 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H)
Published: 2022-10-17
Source: https://osv.dev/vulnerability/CVE-2022-3565
Type: osv

## Details
A vulnerability, which was classified as critical, has been found in Linux Kernel. Affected by this issue is the function del_timer of the file drivers/isdn/mISDN/l1oip_core.c of the component Bluetooth. The manipulation leads to use after free. It is recommended to apply a patch to fix this issue. The identifier of this vulnerability is VDB-211088.

## References
- https://lists.debian.org/debian-lts-announce/2022/12/msg00031.html
- https://lists.debian.org/debian-lts-announce/2022/12/msg00034.html
- https://vuldb.com/?id.211088
- https://git.kernel.org/pub/scm/linux/kernel/git/bluetooth/bluetooth-next.git/commit/?id=2568a7e0832ee30b0a351016d03062ab4e0e0a3f
