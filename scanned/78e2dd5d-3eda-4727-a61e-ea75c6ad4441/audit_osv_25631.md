# [H] Shim: interger overflow leads to heap buffer overflow in verify_sbat_section on 32-bits systems

## Summary
Severity: High
Advisory: CVE-2023-40548
CVSS: 7.4 (CVSS:3.1/AV:L/AC:H/PR:N/UI:N/S:U/C:H/I:H/A:H)
Published: 2024-01-29
Source: https://osv.dev/vulnerability/CVE-2023-40548
Type: osv

## Details
A buffer overflow was found in Shim in the 32-bit system. The overflow happens due to an addition operation involving a user-controlled value parsed from the PE binary being used by Shim. This value is further used for memory allocation operations, leading to a heap-based buffer overflow. This flaw causes memory corruption and can lead to a crash or data integrity issues during the boot phase.

## References
- https://access.redhat.com/downloads/content/package-browser/
- https://lists.debian.org/debian-lts-announce/2024/05/msg00009.html
- https://access.redhat.com/errata/RHSA-2024:1834
- https://access.redhat.com/errata/RHSA-2024:1835
- https://access.redhat.com/errata/RHSA-2024:1873
- https://access.redhat.com/errata/RHSA-2024:1876
- https://access.redhat.com/errata/RHSA-2024:1883
- https://access.redhat.com/errata/RHSA-2024:1902
- https://access.redhat.com/errata/RHSA-2024:1903
- https://access.redhat.com/errata/RHSA-2024:1959
- https://access.redhat.com/errata/RHSA-2024:2086
- https://access.redhat.com/security/cve/CVE-2023-40548
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2023/40xxx/CVE-2023-40548.json
- https://nvd.nist.gov/vuln/detail/CVE-2023-40548
- https://bugzilla.redhat.com/show_bug.cgi?id=2241782
