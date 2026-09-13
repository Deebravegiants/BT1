# [C] OpenShift GitOps authenticated attackers can obtain cluster root access through forged ArgoCD custom resources

## Summary
Severity: Critical
Advisory: GHSA-pcqx-8qww-7f4v
CVE: CVE-2025-13888
CWE: CWE-266
Ecosystem: Go
CVSS: CVSS:3.1/AV:N/AC:L/PR:H/UI:N/S:C/C:H/I:H/A:H (CVSS_V3)
Published: 2025-12-15
Source: https://github.com/advisories/GHSA-pcqx-8qww-7f4v
Type: github-advisory

## Affected
- Go: `github.com/redhat-developer/gitops-operator` — affected >=0 <1.16.2

## Details
A flaw was found in OpenShift GitOps. Namespace admins can create ArgoCD Custom Resources (CRs) that trick the system into granting them elevated permissions in other namespaces, including privileged namespaces. An authenticated attacker can then use these elevated permissions to create privileged workloads that run on master nodes, effectively giving them root access to the entire cluster.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2025-13888
- https://github.com/redhat-developer/gitops-operator/pull/897
- https://github.com/redhat-developer/gitops-operator/commit/bc6ac3e03d7c8b3db5d8f1770c868396a4c2dcef
- https://access.redhat.com/errata/RHSA-2025:23203
- https://access.redhat.com/errata/RHSA-2025:23206
- https://access.redhat.com/errata/RHSA-2025:23207
- https://access.redhat.com/errata/RHSA-2026:1017
- https://access.redhat.com/security/cve/CVE-2025-13888
- https://bugzilla.redhat.com/show_bug.cgi?id=2418361
- https://github.com/redhat-developer/gitops-operator
- https://github.com/redhat-developer/gitops-operator/releases/tag/v1.16.2
