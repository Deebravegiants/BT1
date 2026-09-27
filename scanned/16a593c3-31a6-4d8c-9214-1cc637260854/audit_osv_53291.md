# [H] CVE-2022-3640

## Summary
Severity: High
Advisory: CVE-2022-3640
CVSS: 8.8 (CVSS:3.1/AV:A/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H)
Published: 2022-10-21
Source: https://osv.dev/vulnerability/CVE-2022-3640
Type: osv

## Details
A vulnerability, which was classified as critical, was found in Linux Kernel. Affected is the function l2cap_conn_del of the file net/bluetooth/l2cap_core.c of the component Bluetooth. The manipulation leads to use after free. It is recommended to apply a patch to fix this issue. The identifier of this vulnerability is VDB-211944.

## References
- https://lists.fedoraproject.org/archives/list/package-announce%40lists.fedoraproject.org/message/DGOIRR72OAFE53XZRUDZDP7INGLIC3E3/
- https://lists.fedoraproject.org/archives/list/package-announce%40lists.fedoraproject.org/message/OD7VWUT7YAU4CJ247IF44NGVOAODAJGC/
- https://lists.fedoraproject.org/archives/list/package-announce%40lists.fedoraproject.org/message/XG2UPX3MQ7RKRJEUMGEH2TLPKZJCBU5C/
- https://lists.debian.org/debian-lts-announce/2022/12/msg00031.html
- https://lists.debian.org/debian-lts-announce/2022/12/msg00034.html
- https://vuldb.com/?id.211944
- https://git.kernel.org/pub/scm/linux/kernel/git/bluetooth/bluetooth-next.git/commit/?id=42cf46dea905a80f6de218e837ba4d4cc33d6979
