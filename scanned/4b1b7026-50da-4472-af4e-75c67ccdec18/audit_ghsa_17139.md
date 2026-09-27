# [H] kubevirt-csi: PersistentVolume allows access to HCP's root node

## Summary
Severity: High
Advisory: GHSA-fg9q-5cw2-p6r9
CVE: CVE-2024-1725
CWE: CWE-501
Ecosystem: Go
CVSS: CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:N (CVSS_V3)
Published: 2024-03-07
Source: https://github.com/advisories/GHSA-fg9q-5cw2-p6r9
Type: github-advisory

## Affected
- Go: `github.com/kubevirt/csi-driver` — affected >=0 <0.0.0-202403081943-cc28dcbb0afc14

## Details
A flaw was found in the kubevirt-csi component of OpenShift Virtualization's Hosted Control Plane (HCP). This issue could allow an authenticated attacker to gain access to the root HCP worker node's volume by creating a custom Persistent Volume that matches the name of a worker node.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2024-1725
- https://github.com/kubevirt/csi-driver/commit/cc28dcbb0afca0a7cb8a73bc998ab49f864ed560
- https://access.redhat.com/errata/RHSA-2024:1559
- https://access.redhat.com/errata/RHSA-2024:1891
- https://access.redhat.com/errata/RHSA-2024:2047
- https://access.redhat.com/security/cve/CVE-2024-1725
- https://bugzilla.redhat.com/show_bug.cgi?id=2265398
- https://github.com/kubevirt/csi-driver
- https://pkg.go.dev/vuln/GO-2025-3512
