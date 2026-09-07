# [M] Access Restriction Bypass in kube-apiserver

## Summary
Severity: Medium
Advisory: GHSA-g42g-737j-qx6j
CVE: CVE-2021-25735
CWE: CWE-284, CWE-372, CWE-863
Ecosystem: Go
CVSS: CVSS:3.1/AV:N/AC:L/PR:H/UI:N/S:U/C:N/I:H/A:H (CVSS_V3)
Published: 2021-05-28
Source: https://github.com/advisories/GHSA-g42g-737j-qx6j
Type: github-advisory

## Affected
- Go: `k8s.io/kubernetes` — affected >=1.20.0 <1.20.6
- Go: `k8s.io/kubernetes` — affected >=1.19.0 <1.19.10
- Go: `k8s.io/kubernetes` — affected >=0 <1.18.18

## Details
A vulnerability in Kubernetes `kube-apiserver` could allow node updates to bypass a _Validating Admission Webhook_ and allow unauthorized node updates. The information that is provided to the admission controller could contain old configurations that overwrite values used for validation. Since the overwriting takes place before the validation, this could lead the admission controller to accept requests that should be blocked. The vulnerability can be exploited when an update action on node resources is performed and an admission controller is in place and configured to validate the action.

Users are only affected by this vulnerability if they are running a _Validating Admission Webhook_ for Nodes that denies admission based partially on the old state of the Node object. It only impacts validating admission plugins that rely on old values in certain fields and does not impact calls from kubelets that go through the built-in NodeRestriction admission plugin.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2021-25735
- https://github.com/kubernetes/kubernetes/issues/100096
- https://github.com/kubernetes/kubernetes/pull/99946
- https://github.com/kubernetes/kubernetes/commit/00e81db174ef7aca497be5f42d87e46d14df2a90
- https://bugzilla.redhat.com/show_bug.cgi?id=1937562
- https://github.com/kubernetes/kubernetes
- https://groups.google.com/g/kubernetes-security-announce/c/FKAGqT4jx9Y
- https://pkg.go.dev/k8s.io/kubernetes@v1.23.5/cmd/kube-apiserver
- https://sysdig.com/blog/cve-2021-25735-kubernetes-admission-bypass
