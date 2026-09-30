# [H] CVE-2026-0719

## Summary
Severity: High
Advisory: CVE-2026-0719
CVSS: 8.6 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:L/I:L/A:H)
Published: 2026-01-08
Source: https://osv.dev/vulnerability/CVE-2026-0719
Type: osv

## Details
A flaw was identified in the NTLM authentication handling of the libsoup HTTP library, used by GNOME and other applications for network communication. When processing extremely long passwords, an internal size calculation can overflow due to improper use of signed integers. This results in incorrect memory allocation on the stack, followed by unsafe memory copying. As a result, applications using libsoup may crash unexpectedly, creating a denial-of-service risk.

## References
- https://access.redhat.com/security/cve/CVE-2026-0719
- https://access.redhat.com/errata/RHSA-2026:2528
- https://access.redhat.com/errata/RHSA-2026:2628
- https://access.redhat.com/errata/RHSA-2026:2844
- https://access.redhat.com/errata/RHSA-2026:2008
- https://access.redhat.com/errata/RHSA-2026:2182
- https://access.redhat.com/errata/RHSA-2026:2214
- https://access.redhat.com/errata/RHSA-2026:2529
- https://access.redhat.com/errata/RHSA-2026:1948
- https://access.redhat.com/errata/RHSA-2026:2216
- https://access.redhat.com/errata/RHSA-2026:2006
- https://access.redhat.com/errata/RHSA-2026:2007
- https://access.redhat.com/errata/RHSA-2026:2215
- https://access.redhat.com/errata/RHSA-2026:2402
- https://access.redhat.com/errata/RHSA-2026:2512
- https://access.redhat.com/errata/RHSA-2026:2513
- https://access.redhat.com/errata/RHSA-2026:2514
- https://access.redhat.com/errata/RHSA-2026:2005
- https://access.redhat.com/errata/RHSA-2026:2049
- https://access.redhat.com/errata/RHSA-2026:2396
