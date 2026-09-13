# [M] Util-linux: util-linux: heap buffer overread in setpwnam() when processing 256-byte usernames

## Summary
Severity: Medium
Advisory: CVE-2025-14104
CVSS: 6.1 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:L/I:N/A:H)
Published: 2025-12-05
Source: https://osv.dev/vulnerability/CVE-2025-14104
Type: osv

## Details
A flaw was found in util-linux. This vulnerability allows a heap buffer overread when processing 256-byte usernames, specifically within the `setpwnam()` function, affecting SUID (Set User ID) login-utils utilities writing to the password database.

## References
- https://access.redhat.com/downloads/content/package-browser/
- https://catalog.redhat.com/software/containers/
- https://access.redhat.com/errata/RHSA-2026:1696
- https://access.redhat.com/errata/RHSA-2026:1852
- https://access.redhat.com/errata/RHSA-2026:1913
- https://access.redhat.com/errata/RHSA-2026:2485
- https://access.redhat.com/errata/RHSA-2026:2563
- https://access.redhat.com/errata/RHSA-2026:2737
- https://access.redhat.com/errata/RHSA-2026:2800
- https://access.redhat.com/errata/RHSA-2026:3406
- https://access.redhat.com/errata/RHSA-2026:4943
- https://access.redhat.com/errata/RHSA-2026:7180
- https://access.redhat.com/security/cve/CVE-2025-14104
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2025/14xxx/CVE-2025-14104.json
- https://nvd.nist.gov/vuln/detail/CVE-2025-14104
- https://bugzilla.redhat.com/show_bug.cgi?id=2419369
- https://github.com/util-linux/util-linux
