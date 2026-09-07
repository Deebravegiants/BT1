# [H] Observability Operator is vulnerable to Incorrect Privilege Assignment through its Custom Resource MonitorStack

## Summary
Severity: High
Advisory: GHSA-mj6p-p843-x5wc
CVE: CVE-2025-2843
CWE: CWE-266
Ecosystem: Go
CVSS: CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H (CVSS_V3)
Published: 2025-11-12
Source: https://github.com/advisories/GHSA-mj6p-p843-x5wc
Type: github-advisory

## Affected
- Go: `github.com/rhobs/observability-operator` — affected >=0 <1.3.0

## Details
A flaw was found in the Observability Operator. The Operator creates a ServiceAccount with *ClusterRole* upon deployment of the *Namespace-Scoped* Custom Resource MonitorStack. This issue allows an adversarial Kubernetes Account with only namespaced-level roles, for example, a tenant controlling a namespace, to create a MonitorStack in the authorized namespace and then elevate permission to the cluster level by impersonating the ServiceAccount created by the Operator, resulting in privilege escalation and other issues.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2025-2843
- https://github.com/rhobs/observability-operator/commit/98b927fab755decd6e030ac6af5c005879bab020
- https://access.redhat.com/errata/RHSA-2025:21146
- https://access.redhat.com/security/cve/CVE-2025-2843
- https://bugzilla.redhat.com/show_bug.cgi?id=2355222
- https://github.com/rhobs/observability-operator
- https://github.com/rhobs/observability-operator/releases/tag/v1.3.0
