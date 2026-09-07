# [H] ingress-nginx comment-based nginx configuration injection

## Summary
Severity: High
Advisory: GHSA-f53h-mxv9-cp98
CVE: CVE-2026-4342
CWE: CWE-20
Ecosystem: Go
CVSS: CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H (CVSS_V3)
Published: 2026-03-20
Source: https://github.com/advisories/GHSA-f53h-mxv9-cp98
Type: github-advisory

## Affected
- Go: `k8s.io/ingress-nginx` — affected >=0 <0.0.0-20260319175635-5183b7d86137

## Details
A security issue was discovered in ingress-nginx where a combination of Ingress annotations can be used to inject configuration into nginx. This can lead to arbitrary code execution in the context of the ingress-nginx controller, and disclosure of Secrets accessible to the controller. (Note that in the default installation, the controller can access all Secrets cluster-wide.)

## References
- https://nvd.nist.gov/vuln/detail/CVE-2026-4342
- https://github.com/kubernetes/kubernetes/issues/137893
- https://github.com/kubernetes/ingress-nginx/commit/5183b7d861377a9a2f6d2acaf44f8f6abd5cd0aa
- https://github.com/kubernetes/ingress-nginx
- http://www.openwall.com/lists/oss-security/2026/03/19/9
