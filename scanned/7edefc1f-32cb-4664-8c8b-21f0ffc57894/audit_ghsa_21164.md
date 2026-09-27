# [H] AES OCB fails to encrypt some bytes

## Summary
Severity: High
Advisory: GHSA-3wx7-46ch-7rq2
CVE: CVE-2022-2097
CWE: CWE-311, CWE-326, CWE-327
Ecosystem: crates.io
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:N/A:N (CVSS_V3)
Published: 2022-07-06
Source: https://github.com/advisories/GHSA-3wx7-46ch-7rq2
Type: github-advisory

## Affected
- crates.io: `openssl-src` — affected >=0 <111.22.0
- crates.io: `openssl-src` — affected >=300.0.0 <300.0.9

## Details
AES OCB mode for 32-bit x86 platforms using the AES-NI assembly optimized implementation will not encrypt the entirety of the data under some circumstances.  This could reveal sixteen bytes of data that was pre-existing in the memory that wasn't written.  In the special case of "in place" encryption, sixteen bytes of the plaintext would be revealed.

Since OpenSSL does not support OCB based cipher suites for TLS and DTLS, they are both unaffected.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2022-2097
- https://www.openssl.org/news/secadv/20220705.txt
- https://www.debian.org/security/2023/dsa-5343
- https://security.netapp.com/advisory/ntap-20240621-0006
- https://security.netapp.com/advisory/ntap-20230420-0008
- https://security.netapp.com/advisory/ntap-20220715-0011
- https://security.gentoo.org/glsa/202210-02
- https://rustsec.org/advisories/RUSTSEC-2022-0032.html
- https://lists.fedoraproject.org/archives/list/package-announce@lists.fedoraproject.org/message/VCMNWKERPBKOEBNL7CLTTX3ZZCZLH7XA
- https://lists.fedoraproject.org/archives/list/package-announce@lists.fedoraproject.org/message/V6567JERRHHJW2GNGJGKDRNHR7SNPZK7
- https://lists.fedoraproject.org/archives/list/package-announce@lists.fedoraproject.org/message/R6CK57NBQFTPUMXAPJURCGXUYT76NQAK
- https://lists.fedoraproject.org/archives/list/package-announce%40lists.fedoraproject.org/message/VCMNWKERPBKOEBNL7CLTTX3ZZCZLH7XA
- https://lists.fedoraproject.org/archives/list/package-announce%40lists.fedoraproject.org/message/V6567JERRHHJW2GNGJGKDRNHR7SNPZK7
- https://lists.fedoraproject.org/archives/list/package-announce%40lists.fedoraproject.org/message/R6CK57NBQFTPUMXAPJURCGXUYT76NQAK
- https://lists.debian.org/debian-lts-announce/2023/02/msg00019.html
- https://github.com/alexcrichton/openssl-src-rs
- https://git.openssl.org/gitweb/?p=openssl.git;a=commitdiff;h=a98f339ddd7e8f487d6e0088d4a9a42324885a93
- https://git.openssl.org/gitweb/?p=openssl.git;a=commitdiff;h=919925673d6c9cfed3c1085497f5dfbbed5fc431
- https://git.openssl.org/gitweb/?p=openssl.git%3Ba=commitdiff%3Bh=a98f339ddd7e8f487d6e0088d4a9a42324885a93
- https://git.openssl.org/gitweb/?p=openssl.git%3Ba=commitdiff%3Bh=919925673d6c9cfed3c1085497f5dfbbed5fc431
