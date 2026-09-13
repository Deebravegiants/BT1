# [M] Shim: out-of-bounds read in verify_buffer_authenticode() malformed pe file

## Summary
Severity: Medium
Advisory: CVE-2023-40549
CVSS: 6.2 (CVSS:3.1/AV:L/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:H)
Published: 2024-01-29
Source: https://osv.dev/vulnerability/CVE-2023-40549
Type: osv

## Details
An out-of-bounds read flaw was found in Shim due to the lack of proper boundary verification during the load of a PE binary. This flaw allows an attacker to load a crafted PE binary, triggering the issue and crashing Shim, resulting in a denial of service.

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
- https://access.redhat.com/security/cve/CVE-2023-40549
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2023/40xxx/CVE-2023-40549.json
- https://nvd.nist.gov/vuln/detail/CVE-2023-40549
- https://bugzilla.redhat.com/show_bug.cgi?id=2241797
