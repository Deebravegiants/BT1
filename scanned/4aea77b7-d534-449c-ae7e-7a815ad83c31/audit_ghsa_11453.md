# [M] NFS CSI driver for Kubernetes is Vulnerable to Path Traversal through Volume Identifier Parameter

## Summary
Severity: Medium
Advisory: GHSA-2mjq-54qg-7w6j
CVE: CVE-2026-3864
CWE: CWE-22
Ecosystem: Go
CVSS: CVSS:3.1/AV:N/AC:L/PR:H/UI:N/S:U/C:N/I:H/A:H (CVSS_V3)
Published: 2026-03-21
Source: https://github.com/advisories/GHSA-2mjq-54qg-7w6j
Type: github-advisory

## Affected
- Go: `github.com/kubernetes-csi/csi-driver-nfs` — affected >=0 <0.0.0-20260210055231-316af2d86b91

## Details
A vulnerability was discovered in the Kubernetes CSI Driver for NFS where the subDir parameter in volume identifiers was insufficiently validated. Attackers with the ability to create PersistentVolumes referencing the NFS CSI driver could craft volume identifiers containing path traversal sequences (../). During volume deletion or cleanup operations, the driver could operate on unintended directories outside the intended managed path within the NFS export. This may lead to deletion or modification of directories on the NFS server.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2026-3864
- https://github.com/kubernetes/kubernetes/issues/137797
- https://github.com/kubernetes-csi/csi-driver-nfs/commit/316af2d86b913a595542dc17e8599cf81afd938f
- https://github.com/kubernetes-csi/csi-driver-nfs
- https://groups.google.com/g/kubernetes-security-announce/c/i4ZKN9VLcUE
- http://www.openwall.com/lists/oss-security/2026/03/17/1
