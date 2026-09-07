# [M] Kubernetes ingress exposes sensitive information

## Summary
Severity: Medium
Advisory: GHSA-p3x5-5xpx-9phm
CVE: CVE-2018-1002104
CWE: CWE-20, CWE-215
Ecosystem: Go
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:L/I:N/A:N (CVSS_V3)
Published: 2022-05-24
Source: https://github.com/advisories/GHSA-p3x5-5xpx-9phm
Type: github-advisory

## Affected
- Go: `k8s.io/ingress-nginx` — affected >=0 <1.5

## Details
Versions < 1.5 of the Kubernetes ingress default backend, which handles invalid ingress traffic, exposed prometheus metrics publicly.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2018-1002104
- https://github.com/kubernetes/ingress-nginx/issues/1733
- https://github.com/kubernetes/ingress-nginx/pull/3125
- https://github.com/kubernetes/ingress-nginx/commit/d487a50e399100ad8db12ed1d2f92271f311f676
- https://github.com/kubernetes/ingress-nginx
