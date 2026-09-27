# [H] Open Cluster Management (OCM): Cross-cluster privilege escalation via improper Kubernetes client certificate renewal validation

## Summary
Severity: High
Advisory: GHSA-q4gv-pjmh-c735
CVE: CVE-2026-4740
CWE: CWE-295
Ecosystem: Go
CVSS: CVSS:3.1/AV:L/AC:L/PR:H/UI:N/S:C/C:H/I:H/A:H (CVSS_V3)
Published: 2026-04-07
Source: https://github.com/advisories/GHSA-q4gv-pjmh-c735
Type: github-advisory

## Affected
- Go: `open-cluster-management.io/ocm` — affected >=0 <1.2.1

## Details
A flaw was found in Open Cluster Management (OCM), the technology underlying Red Hat Advanced Cluster Management (ACM). Improper validation of Kubernetes client certificate renewal allows a managed cluster administrator to forge a client certificate that can be approved by the OCM controller. This enables cross-cluster privilege escalation and may allow an attacker to gain control over other managed clusters, including the hub cluster.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2026-4740
- https://github.com/open-cluster-management-io/ocm/commit/9e70cc1e21a15239c81111062c0b37df4b5a8026
- https://access.redhat.com/security/cve/CVE-2026-4740
- https://blog.arfevrier.fr/open-cluster-management-cross-cluster-escape
- https://bugzilla.redhat.com/show_bug.cgi?id=2450590
- https://github.com/open-cluster-management-io/OCM
