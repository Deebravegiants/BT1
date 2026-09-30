# [H] Libarchive: double free at archive_read_format_rar_seek_data() in archive_read_support_format_rar.c

## Summary
Severity: High
Advisory: CVE-2025-5914
CVSS: 7.8 (CVSS:3.1/AV:L/AC:L/PR:N/UI:R/S:U/C:H/I:H/A:H)
Published: 2025-06-09
Source: https://osv.dev/vulnerability/CVE-2025-5914
Type: osv

## Details
A vulnerability has been identified in the libarchive library, specifically within the archive_read_format_rar_seek_data() function. This flaw involves an integer overflow that can ultimately lead to a double-free condition. Exploiting a double-free vulnerability can result in memory corruption, enabling an attacker to execute arbitrary code or cause a denial-of-service condition.

## References
- https://access.redhat.com/downloads/content/package-browser/
- https://catalog.redhat.com/software/containers/
- https://cert-portal.siemens.com/productcert/html/ssa-585531.html
- https://github.com/libarchive/libarchive/
- https://github.com/libarchive/libarchive/releases/tag/v3.8.0
- https://access.redhat.com/errata/RHSA-2025:14130
- https://access.redhat.com/errata/RHSA-2025:14135
- https://access.redhat.com/errata/RHSA-2025:14137
- https://access.redhat.com/errata/RHSA-2025:14141
- https://access.redhat.com/errata/RHSA-2025:14142
- https://access.redhat.com/errata/RHSA-2025:14525
- https://access.redhat.com/errata/RHSA-2025:14528
- https://access.redhat.com/errata/RHSA-2025:14594
- https://access.redhat.com/errata/RHSA-2025:14644
- https://access.redhat.com/errata/RHSA-2025:14808
- https://access.redhat.com/errata/RHSA-2025:14810
- https://access.redhat.com/errata/RHSA-2025:14828
- https://access.redhat.com/errata/RHSA-2025:15024
- https://access.redhat.com/errata/RHSA-2025:15397
- https://access.redhat.com/errata/RHSA-2025:15709
