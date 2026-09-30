# [M] Ose-olm-catalogd-container: incomplete fix for rapid reset (cve-2023-39325/cve-2023-44487)

## Summary
Severity: Medium
Advisory: CVE-2024-12698
CVSS: 6.5 (CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:N/I:N/A:H)
Published: 2024-12-18
Source: https://osv.dev/vulnerability/CVE-2024-12698
Type: osv

## Details
An incomplete fix for ose-olm-catalogd-container was issued for the Rapid Reset Vulnerability (CVE-2023-39325/CVE-2023-44487) where only unauthenticated streams were protected, not streams created by authenticated sources.

## References
- https://catalog.redhat.com/software/containers/
- https://access.redhat.com/errata/RHSA-2024:6122
- https://access.redhat.com/security/cve/CVE-2024-12698
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2024/12xxx/CVE-2024-12698.json
- https://nvd.nist.gov/vuln/detail/CVE-2024-12698
- https://bugzilla.redhat.com/show_bug.cgi?id=2332674
- https://github.com/operator-framework/catalogd
