# [H] CVE-2019-13115

## Summary
Severity: High
Advisory: CVE-2019-13115
CVSS: 8.1 (CVSS:3.1/AV:N/AC:L/PR:N/UI:R/S:U/C:H/I:N/A:H)
Published: 2019-07-16
Source: https://osv.dev/vulnerability/CVE-2019-13115
Type: osv

## Details
In libssh2 before 1.9.0, kex_method_diffie_hellman_group_exchange_sha256_key_exchange in kex.c has an integer overflow that could lead to an out-of-bounds read in the way packets are read from the server. A remote attacker who compromises a SSH server may be able to disclose sensitive information or cause a denial of service condition on the client system when a user connects to the server. This is related to an _libssh2_check_length mistake, and is different from the various issues fixed in 1.8.1, such as CVE-2019-3855.

## References
- http://packetstormsecurity.com/files/172834/libssh2-1.8.2-Out-Of-Bounds-Read.html
- https://lists.apache.org/thread.html/r58af02e294bd07f487e2c64ffc0a29b837db5600e33b6e698b9d696b%40%3Cissues.bookkeeper.apache.org%3E
- https://lists.apache.org/thread.html/rf4c02775860db415b4955778a131c2795223f61cb8c6a450893651e4%40%3Cissues.bookkeeper.apache.org%3E
- https://lists.debian.org/debian-lts-announce/2023/09/msg00006.html
- https://lists.fedoraproject.org/archives/list/package-announce%40lists.fedoraproject.org/message/6LUNHPW64IGCASZ4JQ2J5KDXNZN53DWW/
- https://lists.fedoraproject.org/archives/list/package-announce%40lists.fedoraproject.org/message/M7IF3LNHOA75O4WZWIHJLIRMA5LJUED3/
- https://support.f5.com/csp/article/K13322484?utm_source=f5support&amp%3Butm_medium=RSS
- https://github.com/libssh2/libssh2/compare/02ecf17...42d37aa
- https://libssh2.org/changes.html
- https://lists.debian.org/debian-lts-announce/2019/07/msg00024.html
- https://lists.debian.org/debian-lts-announce/2021/12/msg00013.html
- https://security.netapp.com/advisory/ntap-20190806-0002/
- https://support.f5.com/csp/article/K13322484
- https://github.com/libssh2/libssh2/pull/350
- https://blog.semmle.com/libssh2-integer-overflow/
