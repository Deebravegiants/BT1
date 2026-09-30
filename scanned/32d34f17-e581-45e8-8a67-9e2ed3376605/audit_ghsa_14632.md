# [H] Open Cluster Management vulnerable to Trust Boundary Violation

## Summary
Severity: High
Advisory: GHSA-jhh6-6fhp-q2xp
CVE: CVE-2024-9779
CWE: CWE-266, CWE-501
Ecosystem: Go
CVSS: CVSS:3.1/AV:N/AC:H/PR:N/UI:N/S:C/C:L/I:H/A:N (CVSS_V3)
Published: 2024-12-18
Source: https://github.com/advisories/GHSA-jhh6-6fhp-q2xp
Type: github-advisory

## Affected
- Go: `open-cluster-management.io/ocm` — affected >=0 <0.13.0

## Details
A flaw was found in Open Cluster Management (OCM) when a user has access to the worker nodes which contain the cluster-manager or klusterlet deployments. The cluster-manager deployment uses a service account with the same name "cluster-manager" which is bound to a ClusterRole also named "cluster-manager", which includes the permission to create Pod resources. If this deployment runs a pod on an attacker-controlled node, the attacker can obtain the cluster-manager's token and steal any service account token by creating and mounting the target service account to control the whole cluster.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2024-9779
- https://github.com/open-cluster-management-io/registration-operator/issues/361
- https://github.com/open-cluster-management-io/ocm/pull/325
- https://access.redhat.com/security/cve/CVE-2024-9779
- https://bugzilla.redhat.com/show_bug.cgi?id=2317916
- https://github.com/open-cluster-management-io/OCM
- https://github.com/open-cluster-management-io/ocm/releases/tag/v0.13.0
