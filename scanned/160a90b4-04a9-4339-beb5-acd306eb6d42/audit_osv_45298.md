# [H] A flaw was found in libssh when using the ChaCha20 cipher with the OpenSSL library

## Summary
Severity: High
Advisory: JLSEC-2025-332
Ecosystem: Julia
CVSS: 8.1 (CVSS:3.1/AV:N/AC:H/PR:N/UI:N/S:U/C:H/I:H/A:H)
Published: 2025-12-01
Source: https://osv.dev/vulnerability/JLSEC-2025-332
Type: osv

## Affected
- Julia: `libssh_jll` — affected >=0 <0.11.3+0

## Details
A flaw was found in libssh when using the ChaCha20 cipher with the OpenSSL library. If an attacker manages to exhaust the heap space, this error is not detected and may lead to libssh using a partially initialized cipher context. This occurs because the OpenSSL error code returned aliases with the `SSH_OK` code, resulting in libssh not properly detecting the error returned by the OpenSSL library. This issue can lead to undefined behavior, including compromised data confidentiality and integrity or crashes.

## References
- https://access.redhat.com/errata/RHSA-2025:23483
- https://access.redhat.com/errata/RHSA-2025:23484
- https://access.redhat.com/errata/RHSA-2026:0427
- https://access.redhat.com/errata/RHSA-2026:0428
- https://access.redhat.com/errata/RHSA-2026:0430
- https://access.redhat.com/errata/RHSA-2026:0431
- https://access.redhat.com/errata/RHSA-2026:0702
- https://access.redhat.com/errata/RHSA-2026:0978
- https://access.redhat.com/errata/RHSA-2026:0980
- https://access.redhat.com/errata/RHSA-2026:0985
- https://access.redhat.com/errata/RHSA-2026:0996
- https://access.redhat.com/errata/RHSA-2026:1539
- https://access.redhat.com/errata/RHSA-2026:1541
- https://access.redhat.com/errata/RHSA-2026:3415
- https://access.redhat.com/security/cve/CVE-2025-5987
- https://bugzilla.redhat.com/show_bug.cgi?id=2376219
- https://www.libssh.org/security/advisories/CVE-2025-5987.txt
