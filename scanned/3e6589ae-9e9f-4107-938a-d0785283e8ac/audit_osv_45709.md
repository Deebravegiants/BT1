# [M] Issue summary: The AES-SIV cipher implementation contains a bug that causes it to ignore empty...

## Summary
Severity: Medium
Advisory: JLSEC-2026-240
Ecosystem: Julia
CVSS: 5.3 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:L/A:N)
Published: 2026-04-27
Source: https://osv.dev/vulnerability/JLSEC-2026-240
Type: osv

## Affected
- Julia: `OpenSSL_jll` — affected >=3.0.8+0 <3.0.10+0

## Details
Issue summary: The AES-SIV cipher implementation contains a bug that causes
it to ignore empty associated data entries which are unauthenticated as
a consequence.

Impact summary: Applications that use the AES-SIV algorithm and want to
authenticate empty data entries as associated data can be misled by removing,
adding or reordering such empty entries as these are ignored by the OpenSSL
implementation. We are currently unaware of any such applications.

The AES-SIV algorithm allows for authentication of multiple associated
data entries along with the encryption. To authenticate empty data the
application has to call `EVP_EncryptUpdate()` (or `EVP_CipherUpdate()`) with
NULL pointer as the output buffer and 0 as the input buffer length.
The AES-SIV implementation in OpenSSL just returns success for such a call
instead of performing the associated data authentication operation.
The empty data thus will not be authenticated.

As this issue does not affect non-empty associated data authentication and
we expect it to be rare for an application to use empty associated data
entries this is qualified as Low severity issue.

## References
- http://www.openwall.com/lists/oss-security/2023/07/15/1
- http://www.openwall.com/lists/oss-security/2023/07/19/5
- https://git.openssl.org/gitweb/?p=openssl.git;a=commitdiff;h=00e2f5eea29994d19293ec4e8c8775ba73678598
- https://git.openssl.org/gitweb/?p=openssl.git;a=commitdiff;h=6a83f0c958811f07e0d11dfc6b5a6a98edfd5bdc
- https://github.com/advisories/GHSA-hpqg-7fjp-436p
- https://nvd.nist.gov/vuln/detail/CVE-2023-2975
- https://security.gentoo.org/glsa/202402-08
- https://security.netapp.com/advisory/ntap-20230725-0004
- https://security.netapp.com/advisory/ntap-20230725-0004/
- https://www.openssl.org/news/secadv/20230714.txt
