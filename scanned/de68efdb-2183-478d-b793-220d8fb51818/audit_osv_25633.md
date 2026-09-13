# [M] Shim: out-of-bound read in verify_buffer_sbat()

## Summary
Severity: Medium
Advisory: CVE-2023-40550
CVSS: 5.5 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:H/I:N/A:N)
Published: 2024-01-29
Source: https://osv.dev/vulnerability/CVE-2023-40550
Type: osv

## Details
An out-of-bounds read flaw was found in Shim when it tried to validate the SBAT information. This issue may expose sensitive data during the system's boot phase.

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
- https://access.redhat.com/security/cve/CVE-2023-40550
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2023/40xxx/CVE-2023-40550.json
- https://nvd.nist.gov/vuln/detail/CVE-2023-40550
- https://bugzilla.redhat.com/show_bug.cgi?id=2259915
