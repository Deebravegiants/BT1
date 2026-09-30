# [C] CVE-2021-43267

## Summary
Severity: Critical
Advisory: CVE-2021-43267
Aliases: A-205243414, PUB-A-205243414
CVSS: 9.8 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H)
Published: 2021-11-02
Source: https://osv.dev/vulnerability/CVE-2021-43267
Type: osv

## Details
An issue was discovered in net/tipc/crypto.c in the Linux kernel before 5.14.16. The Transparent Inter-Process Communication (TIPC) functionality allows remote attackers to exploit insufficient validation of user-supplied sizes for the MSG_CRYPTO message type.

## References
- https://lists.fedoraproject.org/archives/list/package-announce%40lists.fedoraproject.org/message/CVWL7HZV5T5OEKJPO2D67RMFMKBBXGGB/
- https://lists.fedoraproject.org/archives/list/package-announce%40lists.fedoraproject.org/message/RDDEW4APTYKJK365HC2JZIVXYUV7ZRN7/
- https://cdn.kernel.org/pub/linux/kernel/v5.x/ChangeLog-5.14.16
- https://security.netapp.com/advisory/ntap-20211125-0002/
- https://github.com/torvalds/linux/commit/fa40d9734a57bcbfa79a280189799f76c88f7bb0
- http://www.openwall.com/lists/oss-security/2022/02/10/1
