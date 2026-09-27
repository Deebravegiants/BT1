# [H] Kubernetes kube-apiserver unauthorized access

## Summary
Severity: High
Advisory: GHSA-fp37-c92q-4pwq
CVE: CVE-2019-11247
CWE: CWE-863
Ecosystem: Go
CVSS: CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:N (CVSS_V3)
Published: 2022-05-24
Source: https://github.com/advisories/GHSA-fp37-c92q-4pwq
Type: github-advisory

## Affected
- Go: `k8s.io/apiextensions-apiserver` — affected >=0.7.0 <0.13.9
- Go: `k8s.io/apiextensions-apiserver` — affected >=0.14.0 <0.14.5
- Go: `k8s.io/apiextensions-apiserver` — affected >=0.15.0 <0.15.2

## Details
The Kubernetes kube-apiserver mistakenly allows access to a cluster-scoped custom resource if the request is made as if the resource were namespaced. Authorizations for the resource accessed in this manner are enforced using roles and role bindings within the namespace, meaning that a user with access only to a resource in one namespace could create, view update or delete the cluster-scoped resource (according to their namespace role privileges). Kubernetes affected versions include versions prior to 1.13.9, versions prior to 1.14.5, versions prior to 1.15.2, and versions 1.7, 1.8, 1.9, 1.10, 1.11, 1.12.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2019-11247
- https://github.com/kubernetes/kubernetes/issues/80983
- https://github.com/kubernetes/kubernetes/pull/80750
- https://github.com/kubernetes/kubernetes/pull/80850
- https://github.com/kubernetes/kubernetes/pull/80851
- https://github.com/kubernetes/kubernetes/pull/80852
- https://github.com/kubernetes/apiextensions-apiserver/commit/b9b7d2b3f32f8edbeb47b8726710eeb868bce196
- https://access.redhat.com/errata/RHBA-2019:2816
- https://access.redhat.com/errata/RHBA-2019:2824
- https://access.redhat.com/errata/RHSA-2019:2690
- https://access.redhat.com/errata/RHSA-2019:2769
- https://github.com/kubernetes/apiextensions-apiserver
- https://groups.google.com/d/msg/kubernetes-security-announce/vUtEcSEY6SM/v2ZZxsmtFQAJ
- https://security.netapp.com/advisory/ntap-20190919-0003
