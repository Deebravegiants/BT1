# [H] Heap Use-After-Free in the PKCS7_verify() Function

## Summary
Severity: High
Advisory: CVE-2026-45447
CVSS: 8.8 (CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H)
Published: 2026-06-09
Source: https://osv.dev/vulnerability/CVE-2026-45447
Type: osv

## Details
Issue summary: A specially crafted PKCS#7 or S/MIME signed message could
trigger a use-after-free during PKCS#7 signature verification.

Impact summary: A use-after-free may result in process crashes, heap
corruption, or potentially remote code execution.

When processing a PKCS#7 or S/MIME signed message, if the SignedData
digestAlgorithms field is present as an empty ASN.1 SET, OpenSSL may
incorrectly free a caller-owned BIO during PKCS7_verify(). A subsequent
use of the BIO by the calling application results in a use-after-free
condition.

In the common case this occurs when the application later calls
BIO_free() on the BIO originally passed to PKCS7_verify(). Depending
on allocator behavior and application-specific BIO usage patterns, this
may result in a crash or other memory corruption. In some application
contexts this may potentially be exploitable for remote code execution.

Applications that process PKCS#7 or S/MIME signed messages using OpenSSL
PKCS#7 APIs may be affected. Applications using the CMS APIs for this
processing are not affected.

The FIPS modules in 4.0, 3.6, 3.5, 3.4, and 3.0 are not affected by this
issue, as the affected code is outside the OpenSSL FIPS module boundary.

## References
- https://security.access.redhat.com/data/csaf/v2/vex/2026/cve-2026-45447.json
- https://access.redhat.com/errata/RHSA-2026:25237
- https://access.redhat.com/errata/RHSA-2026:25239
- https://access.redhat.com/errata/RHSA-2026:26275
- https://access.redhat.com/errata/RHSA-2026:26319
- https://access.redhat.com/errata/RHSA-2026:29197
- https://access.redhat.com/errata/RHSA-2026:34102
- https://access.redhat.com/errata/RHSA-2026:35869
- https://access.redhat.com/errata/RHSA-2026:36215
- https://access.redhat.com/errata/RHSA-2026:36217
- https://access.redhat.com/errata/RHSA-2026:39009
- https://access.redhat.com/errata/RHSA-2026:39012
- https://access.redhat.com/errata/RHSA-2026:39981
- https://access.redhat.com/errata/RHSA-2026:44438
- https://access.redhat.com/errata/RHSA-2026:47735
- https://access.redhat.com/errata/RHSA-2026:47737
- https://access.redhat.com/errata/RHSA-2026:58563
- https://access.redhat.com/errata/RHSA-2026:58981
- https://access.redhat.com/errata/RHSA-2026:59831
- https://access.redhat.com/errata/RHSA-2026:66524
