# [H] CVE-2021-46790

## Summary
Severity: High
Advisory: CVE-2021-46790
CVSS: 7.8 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H)
Published: 2022-05-02
Source: https://osv.dev/vulnerability/CVE-2021-46790
Type: osv

## Details
ntfsck in NTFS-3G through 2021.8.22 has a heap-based buffer overflow involving buffer+512*3-2. NOTE: the upstream position is that ntfsck is deprecated; however, it is shipped by some Linux distributions.

## References
- https://lists.fedoraproject.org/archives/list/package-announce%40lists.fedoraproject.org/message/7JPX6OUCQKZX4PN5DQPVDUFZCOOZUX7Z/
- https://lists.fedoraproject.org/archives/list/package-announce%40lists.fedoraproject.org/message/ECDCISL24TYH4CTDFCUVF24WAKRSYF7F/
- https://lists.fedoraproject.org/archives/list/package-announce%40lists.fedoraproject.org/message/FAXFYIJWT5SHHRNPOJETM77EIMJ6ZP6I/
- https://lists.fedoraproject.org/archives/list/package-announce%40lists.fedoraproject.org/message/UEXHDCUSLJD2HSPMAAVZ5AWMPUOG6UI7/
- http://www.openwall.com/lists/oss-security/2022/05/26/1
- https://www.debian.org/security/2022/dsa-5160
- https://github.com/tuxera/ntfs-3g/issues/16
