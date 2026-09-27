# [M] ALPINE-CVE-2023-2975

## Summary
Severity: Medium
Advisory: ALPINE-CVE-2023-2975
Ecosystem: Alpine:v3.15, Alpine:v3.16, Alpine:v3.17, Alpine:v3.18, Alpine:v3.19, Alpine:v3.20, Alpine:v3.21, Alpine:v3.22, Alpine:v3.23, Alpine:v3.24
CVSS: 5.3 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:L/A:N)
Published: 2023-07-14
Source: https://osv.dev/vulnerability/ALPINE-CVE-2023-2975
Type: osv

## Affected
- Alpine:v3.17: `openssl` — affected >=3.0.0 <3.0.9-r2
- Alpine:v3.18: `openssl` — affected >=3.0.0 <3.1.1-r2
- Alpine:v3.19: `openssl` — affected >=3.0.0 <3.1.1-r2
- Alpine:v3.20: `openssl` — affected >=3.0.0 <3.1.1-r2
- Alpine:v3.21: `openssl` — affected >=3.0.0 <3.1.1-r2
- Alpine:v3.22: `openssl` — affected >=3.0.0 <3.1.1-r2
- Alpine:v3.23: `openssl` — affected >=3.0.0 <3.1.1-r2
- Alpine:v3.24: `openssl` — affected >=3.0.0 <3.1.1-r2
- Alpine:v3.15: `openssl3` — affected >=0 <3.0.9-r1
- Alpine:v3.16: `openssl3` — affected >=0 <3.0.9-r1

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
application has to call EVP_EncryptUpdate() (or EVP_CipherUpdate()) with
NULL pointer as the output buffer and 0 as the input buffer length.
The AES-SIV implementation in OpenSSL just returns success for such a call
instead of performing the associated data authentication operation.
The empty data thus will not be authenticated.

As this issue does not affect non-empty associated data authentication and
we expect it to be rare for an application to use empty associated data
entries this is qualified as Low severity issue.

## References
- https://security.alpinelinux.org/vuln/CVE-2023-2975
