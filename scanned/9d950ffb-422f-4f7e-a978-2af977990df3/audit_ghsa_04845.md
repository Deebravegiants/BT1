# [M] Grafana Operator: Privilege escalation from namespace admin to cluster admin via GrafanaDashboard jsonnetLib fileName

## Summary
Severity: Medium
Advisory: GHSA-fcw4-wwqm-m8cf
CVE: CVE-2026-11769
CWE: CWE-200, CWE-22
Ecosystem: Go
CVSS: CVSS:4.0/AV:N/AC:L/AT:N/PR:L/UI:N/VC:N/VI:N/VA:N/SC:H/SI:H/SA:N (CVSS_V4)
Published: 2026-06-19
Source: https://github.com/advisories/GHSA-fcw4-wwqm-m8cf
Type: github-advisory

## Affected
- Go: `github.com/grafana/grafana-operator/v5` — affected >=0 <5.24.0
- Go: `github.com/grafana/grafana-operator` — affected >=0

## Details
We have released version 5.24.0 of the Grafana Operator. This patch includes a MODERATE severity security fix for a path traversal/privilege escalation vulnerability in the Grafana Operator.


### Summary

The Grafana Operator supports loading dashboards & library panels using the jsonnet data templating language. The jsonnet expression is evaluated in the context of the operator manager pod.
### Impact

It is possible for a malicious user who can create `Dashboard` or `LibraryPanel` resources for a `Grafana` instance to obtain the Kubernetes service account token of the Grafana Operator manager.

### Affected versions

All Grafana Operator versions <= 5.23

### Solutions and mitigations

All installations should be upgraded as soon as possible.

As a workaround, the following ValidatingAdmissionPolicy prevent the creation or modification of jsonnet based resources:
```
apiVersion: admissionregistration.k8s.io/v1
kind: ValidatingAdmissionPolicy
metadata:
  name: "prevent-jsonnet-dashboards"
spec:
  failurePolicy: Fail
  matchConstraints:
    resourceRules:
      - apiGroups: ["grafana.integreatly.org"]
        apiVersions: ["v1beta1"]
        operations: ["CREATE", "UPDATE"]
        resources: ["grafanadashboards", "grafanalibrarypanels"]
  validations:
    - expression: "!has(object.spec.jsonnetLib)"
---
apiVersion: admissionregistration.k8s.io/v1
kind: ValidatingAdmissionPolicyBinding
metadata:
  name: "prevent-jsonnet-dashboards-clusterwide"
spec:
  policyName: "prevent-jsonnet-dashboards"
  validationActions: [Deny]
```


### Acknowledgement

We would like to thank [Artem Cherezov](https://github.com/cherez0ff) for responsibly disclosing the vulnerability.

## References
- https://github.com/grafana/grafana-operator/security/advisories/GHSA-fcw4-wwqm-m8cf
- https://nvd.nist.gov/vuln/detail/CVE-2026-11769
- https://github.com/grafana/grafana-operator
- https://grafana.com/security/security-advisories/cve-2026-11769
