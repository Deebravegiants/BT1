# [H] OpenShift GitOps Operator Namespace Isolation Break

## Summary
Severity: High
Advisory: GHSA-58fx-7v9q-3g56
CVE: CVE-2024-13484
CWE: CWE-668
Ecosystem: Go
CVSS: CVSS:3.1/AV:L/AC:L/PR:H/UI:N/S:C/C:H/I:H/A:H (CVSS_V3)
Published: 2025-01-28
Source: https://github.com/advisories/GHSA-58fx-7v9q-3g56
Type: github-advisory

## Affected
- Go: `github.com/redhat-developer/gitops-operator` — affected >=0 <1.16.2

## Details
A flaw was found in openshift-gitops-operator-container. The openshift.io/cluster-monitoring label is applied to all namespaces that deploy an ArgoCD CR instance, allowing the namespace to create a rogue PrometheusRule. This issue can have adverse effects on the platform monitoring stack, as the rule is rolled out cluster-wide when the label is applied.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2024-13484
- https://github.com/redhat-developer/gitops-operator/pull/853
- https://github.com/redhat-developer/gitops-operator/pull/867
- https://github.com/redhat-developer/gitops-operator/pull/868
- https://github.com/redhat-developer/gitops-operator/pull/869
- https://github.com/redhat-developer/gitops-operator/pull/897
- https://github.com/redhat-developer/gitops-operator/commit/bc6ac3e03d7c8b3db5d8f1770c868396a4c2dcef
- https://access.redhat.com/errata/RHSA-2025:7753
- https://access.redhat.com/errata/RHSA-2025:8274
- https://access.redhat.com/errata/RHSA-2025:9506
- https://access.redhat.com/security/cve/CVE-2024-13484
- https://bugzilla.redhat.com/show_bug.cgi?id=2269376
- https://github.com/argoproj/argo-cd
- https://issues.redhat.com/browse/GITOPS-7037
- https://pkg.go.dev/vuln/GO-2025-3427
