# [H] Libsolv: heap buffer overflow in libsolv repopagestore via unchecked decompression of malicious .solv page data

## Summary
Severity: High
Advisory: CVE-2026-48864
CVSS: 7.8 (CVSS:3.1/AV:L/AC:L/PR:N/UI:R/S:U/C:H/I:H/A:H)
Published: 2026-05-26
Source: https://osv.dev/vulnerability/CVE-2026-48864
Type: osv

## Details
A flaw was found in libsolv. This heap buffer overflow occurs during the decompression of attacker-controlled compressed data within `.solv` files due to insufficient input validation. An attacker can provide a specially crafted `.solv` file, which, when processed by a vulnerable application, can lead to out-of-bounds memory access. This could result in information disclosure, alteration of program execution, or a denial of service.

## References
- https://access.redhat.com/downloads/content/package-browser/
- https://catalog.redhat.com/software/containers/
- https://access.redhat.com/errata/RHSA-2026:21333
- https://access.redhat.com/errata/RHSA-2026:28236
- https://access.redhat.com/errata/RHSA-2026:36730
- https://access.redhat.com/errata/RHSA-2026:39315
- https://access.redhat.com/errata/RHSA-2026:44481
- https://access.redhat.com/errata/RHSA-2026:46836
- https://access.redhat.com/errata/RHSA-2026:48811
- https://access.redhat.com/errata/RHSA-2026:48813
- https://access.redhat.com/errata/RHSA-2026:48814
- https://access.redhat.com/errata/RHSA-2026:48815
- https://access.redhat.com/errata/RHSA-2026:48816
- https://access.redhat.com/errata/RHSA-2026:48817
- https://access.redhat.com/errata/RHSA-2026:48818
- https://access.redhat.com/errata/RHSA-2026:49775
- https://access.redhat.com/errata/RHSA-2026:50223
- https://access.redhat.com/errata/RHSA-2026:53371
- https://access.redhat.com/errata/RHSA-2026:56786
- https://access.redhat.com/errata/RHSA-2026:56853
