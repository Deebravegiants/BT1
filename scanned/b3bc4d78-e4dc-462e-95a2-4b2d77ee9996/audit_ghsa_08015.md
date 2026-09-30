# [H] ingress-nginx's `rules.http.paths.path` Ingress field can be used to inject configuration into nginx

## Summary
Severity: High
Advisory: GHSA-jx8c-56mg-h6vp
CVE: CVE-2026-24512
CWE: CWE-20
Ecosystem: Go
CVSS: CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H (CVSS_V3)
Published: 2026-02-04
Source: https://github.com/advisories/GHSA-jx8c-56mg-h6vp
Type: github-advisory

## Affected
- Go: `k8s.io/ingress-nginx` — affected >=0 <1.13.7
- Go: `k8s.io/ingress-nginx` — affected >=1.14.0 <1.14.3

## Details
A security issue was discovered in ingress-nginx. Tthe `rules.http.paths.path` Ingress field can be used to inject configuration into nginx. This can lead to arbitrary code execution in the context of the ingress-nginx controller, and disclosure of Secrets accessible to the controller. (Note that in the default installation, the controller can access all Secrets cluster-wide.)

## References
- https://nvd.nist.gov/vuln/detail/CVE-2026-24512
- https://github.com/kubernetes/kubernetes/issues/136678
- https://github.com/kubernetes/ingress-nginx
