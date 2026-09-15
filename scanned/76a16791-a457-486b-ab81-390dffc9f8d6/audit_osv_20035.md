# [H] CVE-2021-29477

## Summary
Severity: High
Advisory: CVE-2021-29477
Aliases: GHSA-vqxj-26vj-996g
CVSS: 8.8 (CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H)
Published: 2021-05-04
Source: https://osv.dev/vulnerability/CVE-2021-29477
Type: osv

## Details
Redis is an open source (BSD licensed), in-memory data structure store, used as a database, cache, and message broker. An integer overflow bug in Redis version 6.0 or newer could be exploited using the `STRALGO LCS` command to corrupt the heap and potentially result with remote code execution. The problem is fixed in version 6.2.3 and 6.0.13. An additional workaround to mitigate the problem without patching the redis-server executable is to use ACL configuration to prevent clients from using the `STRALGO LCS` command.

## References
- https://lists.fedoraproject.org/archives/list/package-announce%40lists.fedoraproject.org/message/BHWOF7CBVUGDK3AN6H3BN3VNTH2TDUZZ/
- https://lists.fedoraproject.org/archives/list/package-announce%40lists.fedoraproject.org/message/BPWBIZXA67JFIB63W2CNVVILCGIC2ME5/
- https://lists.fedoraproject.org/archives/list/package-announce%40lists.fedoraproject.org/message/EZJ6JGQ2ETZB2DWTQSGCOGG7EF3ILV4V/
- https://lists.fedoraproject.org/archives/list/package-announce%40lists.fedoraproject.org/message/SN7INTZFE34MIQJO7WDDTIY5LIBGN6GI/
- https://redis.io/
- https://github.com/redis/redis/security/advisories/GHSA-vqxj-26vj-996g
- https://security.gentoo.org/glsa/202107-20
