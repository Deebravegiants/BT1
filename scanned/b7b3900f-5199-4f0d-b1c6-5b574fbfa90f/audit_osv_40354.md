# [H] crypto: ccp - copy IV using skcipher ivsize

## Summary
Severity: High
Advisory: CVE-2026-53016
Ecosystem: Linux
CVSS: 7.8 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H)
Published: 2026-06-24
Source: https://osv.dev/vulnerability/CVE-2026-53016
Type: osv

## Affected
- Linux: `Kernel` — affected >=3.14.0 <5.10.258, >=5.11.0 <5.15.209, >=5.16.0 <6.1.175, >=6.2.0 <6.6.141, >=6.7.0 <6.12.91, >=6.13.0 <6.18.33, >=6.19.0 <7.0.10

## Details
In the Linux kernel, the following vulnerability has been resolved:

crypto: ccp - copy IV using skcipher ivsize

AF_ALG rfc3686-ctr-aes-ccp requests pass an 8-byte IV to the driver.

ccp_aes_complete() restores AES_BLOCK_SIZE bytes into the caller's IV
buffer while RFC3686 skciphers expose an 8-byte IV, so the restore
overruns the provided buffer.

Use crypto_skcipher_ivsize() to copy only the algorithm's IV length.

## References
- https://git.kernel.org/stable/c/227c1e1d9e2aa4cfc65ba446d5690da1f546cda4
- https://git.kernel.org/stable/c/798d409a8949f3f495f238549b86de2886b129bd
- https://git.kernel.org/stable/c/939061b2d0f7f15114e34b4ce878ef50ff4089c3
- https://git.kernel.org/stable/c/a7a1f3cdd64d8a165d9b8c9e9ad7fb46ac19dfc4
- https://git.kernel.org/stable/c/bb01d8f1f385bc9034ca114d3508c7fdea24fc9a
- https://git.kernel.org/stable/c/df9784bb5b637ac80f4a2768a58ca9a50bef28a9
- https://git.kernel.org/stable/c/dfb2cf434829819268fe50f41542aad318ad62b2
- https://git.kernel.org/stable/c/eecee15e263ccb8cd77170a56ab6c969cb54dd6a
- https://security.access.redhat.com/data/csaf/v2/vex/2026/cve-2026-53016.json
- https://access.redhat.com/errata/RHSA-2026:38491
- https://access.redhat.com/errata/RHSA-2026:39494
- https://access.redhat.com/errata/RHSA-2026:55764
- https://access.redhat.com/errata/RHSA-2026:55765
- https://access.redhat.com/errata/RHSA-2026:56574
- https://access.redhat.com/errata/RHSA-2026:59473
- https://access.redhat.com/errata/RHSA-2026:59544
- https://access.redhat.com/errata/RHSA-2026:61256
- https://access.redhat.com/errata/RHSA-2026:64767
- https://access.redhat.com/errata/RHSA-2026:65710
- https://access.redhat.com/security/cve/CVE-2026-53016
