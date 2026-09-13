# [H] CVE-2022-3564

## Summary
Severity: High
Advisory: CVE-2022-3564
CVSS: 7.1 (CVSS:3.1/AV:A/AC:H/PR:L/UI:N/S:U/C:H/I:H/A:H)
Published: 2022-10-17
Source: https://osv.dev/vulnerability/CVE-2022-3564
Type: osv

## Details
A vulnerability classified as critical was found in Linux Kernel. Affected by this vulnerability is the function l2cap_reassemble_sdu of the file net/bluetooth/l2cap_core.c of the component Bluetooth. The manipulation leads to use after free. It is recommended to apply a patch to fix this issue. The associated identifier of this vulnerability is VDB-211087.

## References
- https://lists.debian.org/debian-lts-announce/2022/12/msg00031.html
- https://lists.debian.org/debian-lts-announce/2022/12/msg00034.html
- https://security.netapp.com/advisory/ntap-20221223-0001/
- https://vuldb.com/?id.211087
- https://git.kernel.org/pub/scm/linux/kernel/git/bluetooth/bluetooth-next.git/commit/?id=89f9f3cb86b1c63badaf392a83dd661d56cc50b1
