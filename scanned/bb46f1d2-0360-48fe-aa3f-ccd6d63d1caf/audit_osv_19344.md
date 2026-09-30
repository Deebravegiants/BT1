# [M] CVE-2021-20257

## Summary
Severity: Medium
Advisory: CVE-2021-20257
CVSS: 6.5 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:C/C:N/I:N/A:H)
Published: 2022-03-16
Source: https://osv.dev/vulnerability/CVE-2021-20257
Type: osv

## Details
An infinite loop flaw was found in the e1000 NIC emulator of the QEMU. This issue occurs while processing transmits (tx) descriptors in process_tx_desc if various descriptor fields are initialized with invalid values. This flaw allows a guest to consume CPU cycles on the host, resulting in a denial of service. The highest threat from this vulnerability is to system availability.

## References
- https://lists.debian.org/debian-lts-announce/2022/09/msg00008.html
- https://security.gentoo.org/glsa/202208-27
- https://security.netapp.com/advisory/ntap-20220425-0003/
- https://bugzilla.redhat.com/show_bug.cgi?id=1930087
- https://github.com/qemu/qemu/commit/3de46e6fc489c52c9431a8a832ad8170a7569bd8
- https://lists.gnu.org/archive/html/qemu-devel/2021-02/msg07428.html
- https://www.openwall.com/lists/oss-security/2021/02/25/2
