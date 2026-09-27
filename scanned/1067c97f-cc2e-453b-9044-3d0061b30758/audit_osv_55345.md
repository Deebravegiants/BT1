# [H] CVE-2025-32990

## Summary
Severity: High
Advisory: CVE-2025-32990
CVSS: 8.2 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:L/A:H)
Published: 2025-07-10
Source: https://osv.dev/vulnerability/CVE-2025-32990
Type: osv

## Details
A heap-buffer-overflow (off-by-one) flaw was found in the GnuTLS software in the template parsing logic within the certtool utility. When it reads certain settings from a template file, it allows an attacker to cause an out-of-bounds (OOB) NULL pointer write, resulting in memory corruption and a denial-of-service (DoS) that could potentially crash the system.

## References
- http://www.openwall.com/lists/oss-security/2025/07/11/3
- https://lists.debian.org/debian-lts-announce/2025/08/msg00005.html
- https://access.redhat.com/errata/RHSA-2025:16115
- https://access.redhat.com/errata/RHSA-2025:17361
- https://access.redhat.com/errata/RHSA-2025:17415
- https://access.redhat.com/errata/RHSA-2025:19088
- https://access.redhat.com/errata/RHSA-2025:22529
- https://access.redhat.com/errata/RHSA-2025:16116
- https://access.redhat.com/errata/RHSA-2025:17181
- https://access.redhat.com/errata/RHSA-2025:17348
- https://access.redhat.com/security/cve/CVE-2025-32990
- https://bugzilla.redhat.com/show_bug.cgi?id=2359620
