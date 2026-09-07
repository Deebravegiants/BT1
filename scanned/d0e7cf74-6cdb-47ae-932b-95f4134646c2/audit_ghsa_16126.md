# [H] Kubernetes Nil pointer dereference in KCM after v1 HPA patch request

## Summary
Severity: High
Advisory: GHSA-h7wq-jj8r-qm7p
CVE: CVE-2024-0793
CWE: CWE-20, CWE-476
Ecosystem: Go
CVSS: CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:C/C:N/I:N/A:H (CVSS_V3)
Published: 2024-11-17
Source: https://github.com/advisories/GHSA-h7wq-jj8r-qm7p
Type: github-advisory

## Affected
- Go: `k8s.io/kubernetes` — affected >=0 <1.27.0-alpha.1

## Details
A flaw was found in kube-controller-manager. This issue occurs when the initial application of a HPA config YAML lacking a .spec.behavior.scaleUp block causes a denial of service due to KCM pods going into restart churn.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2024-0793
- https://github.com/kubernetes/kubernetes/issues/107038#issuecomment-1911327145
- https://github.com/openshift/kubernetes/pull/1876
- https://access.redhat.com/errata/RHSA-2024:0741
- https://access.redhat.com/errata/RHSA-2024:1267
- https://access.redhat.com/security/cve/CVE-2024-0793
- https://bugzilla.redhat.com/show_bug.cgi?id=2214402
- https://github.com/kubernetes/kubernetes
- https://pkg.go.dev/vuln/GO-2024-3277
