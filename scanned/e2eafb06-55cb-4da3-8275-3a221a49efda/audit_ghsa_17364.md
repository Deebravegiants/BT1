# [M] kube-controller-manager is vulnerable to half-blind Server Side Request Forgery through in-tree Portworx StorageClass

## Summary
Severity: Medium
Advisory: GHSA-r6j8-c6r2-37rr
CVE: CVE-2025-13281
CWE: CWE-918
Ecosystem: Go
CVSS: CVSS:3.1/AV:N/AC:H/PR:H/UI:N/S:C/C:H/I:N/A:N (CVSS_V3)
Published: 2025-12-15
Source: https://github.com/advisories/GHSA-r6j8-c6r2-37rr
Type: github-advisory

## Affected
- Go: `k8s.io/kubernetes` — affected >=0 <1.32.10
- Go: `k8s.io/kubernetes` — affected >=1.33.0-alpha.0 <1.33.6
- Go: `k8s.io/kubernetes` — affected >=1.34.0-alpha.0 <1.34.2

## Details
A half-blind Server Side Request Forgery (SSRF) vulnerability exists in kube-controller-manager when using the in-tree Portworx StorageClass. This vulnerability allows authorized users to leak arbitrary information from unprotected endpoints in the control plane’s host network (including link-local or loopback services).

## References
- https://nvd.nist.gov/vuln/detail/CVE-2025-13281
- https://github.com/kubernetes/kubernetes/issues/135525
- https://github.com/kubernetes/kubernetes/commit/7506ce804c20696ba32cdb72126270ceaed06e24
- https://github.com/kubernetes/kubernetes/commit/97650c1c4fe15cbb7756ba95b3edc8a8665063ca
- https://github.com/kubernetes/kubernetes/commit/dbe17dfe7773563eac95534040f413ada6d2b421
- https://github.com/advisories/GHSA-r6j8-c6r2-37rr
- https://github.com/kubernetes/kubernetes
- https://groups.google.com/g/kubernetes-security-announce/c/EORqZg0k1l4/m/TtD-q0v7AgAJ
- http://www.openwall.com/lists/oss-security/2025/12/01/4
