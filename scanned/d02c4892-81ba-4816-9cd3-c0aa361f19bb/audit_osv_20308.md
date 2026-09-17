# [H] CVE-2021-32761

## Summary
Severity: High
Advisory: CVE-2021-32761
Aliases: GHSA-8wxq-j7rp-g8wj
CVSS: 7.5 (CVSS:3.1/AV:N/AC:H/PR:L/UI:N/S:U/C:H/I:H/A:H)
Published: 2021-07-21
Source: https://osv.dev/vulnerability/CVE-2021-32761
Type: osv

## Details
Redis is an in-memory database that persists on disk. A vulnerability involving out-of-bounds read and integer overflow to buffer overflow exists starting with version 2.2 and prior to versions 5.0.13, 6.0.15, and 6.2.5. On 32-bit systems, Redis `*BIT*` command are vulnerable to integer overflow that can potentially be exploited to corrupt the heap, leak arbitrary heap contents or trigger remote code execution. The vulnerability involves changing the default `proto-max-bulk-len` configuration parameter to a very large value and constructing specially crafted commands bit commands. This problem only affects Redis on 32-bit platforms, or compiled as a 32-bit binary. Redis versions 5.0.`3m 6.0.15, and 6.2.5 contain patches for this issue. An additional workaround to mitigate the problem without patching the `redis-server` executable is to prevent users from modifying the `proto-max-bulk-len` configuration parameter. This can be done using ACL to restrict unprivileged users from using the CONFIG SET command.

## References
- https://lists.fedoraproject.org/archives/list/package-announce%40lists.fedoraproject.org/message/6O7AUOROBYGP5IMGJPC5HZ3R2RB6GZ5X/
- https://lists.fedoraproject.org/archives/list/package-announce%40lists.fedoraproject.org/message/VGX7RRAWGXWXEAKJTQYSDSBO2BC3SAHD/
- https://github.com/redis/redis/security/advisories/GHSA-8wxq-j7rp-g8wj
- https://lists.debian.org/debian-lts-announce/2021/07/msg00017.html
- https://lists.debian.org/debian-lts-announce/2021/08/msg00026.html
- https://security.gentoo.org/glsa/202209-17
- https://security.netapp.com/advisory/ntap-20210827-0004/
- https://www.debian.org/security/2021/dsa-5001
