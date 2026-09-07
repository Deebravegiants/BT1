# [M] Kubernetes CSI Sidecar Containers Can Allow Unauthorized Data Access

## Summary
Severity: Medium
Advisory: GHSA-f4w6-3rh6-6q4q
CVE: CVE-2019-11255
CWE: CWE-20
Ecosystem: Go
CVSS: CVSS:3.1/AV:N/AC:L/PR:H/UI:N/S:U/C:H/I:H/A:N (CVSS_V3)
Published: 2022-05-24
Source: https://github.com/advisories/GHSA-f4w6-3rh6-6q4q
Type: github-advisory

## Affected
- Go: `github.com/kubernetes-csi/external-provisioner` — affected >=0 <0.4.3
- Go: `github.com/kubernetes-csi/external-provisioner` — affected >=1.0.0 <1.0.2
- Go: `github.com/kubernetes-csi/external-provisioner` — affected 1.1
- Go: `github.com/kubernetes-csi/external-provisioner` — affected >=1.2.0 <1.2.2
- Go: `github.com/kubernetes-csi/external-provisioner` — affected >=1.3.0 <1.3.1
- Go: `github.com/kubernetes-csi/external-snapshotter/v6` — affected >=1.0.0 <1.0.2
- Go: `github.com/kubernetes-csi/external-snapshotter/v6` — affected 1.1
- Go: `github.com/kubernetes-csi/external-snapshotter/v6` — affected >=1.2.0 <1.2.2
- Go: `github.com/kubernetes-csi/external-resizer` — affected 0.1
- Go: `github.com/kubernetes-csi/external-resizer` — affected 0.2

## Details
Improper input validation in Kubernetes CSI sidecar containers for external-provisioner (<v0.4.3, <v1.0.2, v1.1, <v1.2.2, <v1.3.1), external-snapshotter (<v0.4.2, <v1.0.2, v1.1, <1.2.2), and external-resizer (v0.1, v0.2) could result in unauthorized PersistentVolume data access or volume mutation during snapshot, restore from snapshot, cloning and resizing operations.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2019-11255
- https://github.com/kubernetes/kubernetes/issues/85233
- https://access.redhat.com/errata/RHSA-2019:4054
- https://access.redhat.com/errata/RHSA-2019:4096
- https://access.redhat.com/errata/RHSA-2019:4099
- https://access.redhat.com/errata/RHSA-2019:4225
- https://groups.google.com/forum/#!topic/kubernetes-security-announce/aXiYN0q4uIw
- https://security.netapp.com/advisory/ntap-20200810-0003
