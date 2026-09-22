# [M] NULL Pointer Dereference in Kubernetes CSI snapshot-controller

## Summary
Severity: Medium
Advisory: GHSA-hwrr-rhmm-vcvf
CVE: CVE-2020-8569
CWE: CWE-476
Ecosystem: Go
CVSS: CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:N/I:N/A:H (CVSS_V3)
Published: 2022-02-15
Source: https://github.com/advisories/GHSA-hwrr-rhmm-vcvf
Type: github-advisory

## Affected
- Go: `github.com/kubernetes-csi/external-snapshotter/v2` — affected >=2.0.0 <2.1.3
- Go: `github.com/kubernetes-csi/external-snapshotter/v3` — affected >=3.0.0 <3.0.2

## Details
Kubernetes CSI snapshot-controller prior to v2.1.3 and v3.0.2 could panic when processing a VolumeSnapshot custom resource when:

- The VolumeSnapshot referenced a non-existing PersistentVolumeClaim and the VolumeSnapshot did not reference any VolumeSnapshotClass.
- The snapshot-controller crashes, is automatically restarted by Kubernetes, and processes the same VolumeSnapshot custom resource after the restart, entering an endless crashloop.

Only the volume snapshot feature is affected by this vulnerability. When exploited, users canâ€™t take snapshots of their volumes or delete the snapshots. All other Kubernetes functionality is not affected.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2020-8569
- https://github.com/kubernetes-csi/external-snapshotter/issues/380
- https://groups.google.com/g/kubernetes-security-announce/c/1EzCr1qUxxU
