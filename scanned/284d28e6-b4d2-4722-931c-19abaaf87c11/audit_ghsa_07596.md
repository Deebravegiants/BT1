# [M] ingress-nginx vulnerable to Allocation of Resources Without Limits or Throttling 

## Summary
Severity: Medium
Advisory: GHSA-2pf9-vr92-6h3v
CVE: CVE-2026-24514
CWE: CWE-770
Ecosystem: Go
CVSS: CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:N/I:N/A:H (CVSS_V3)
Published: 2026-02-04
Source: https://github.com/advisories/GHSA-2pf9-vr92-6h3v
Type: github-advisory

## Affected
- Go: `k8s.io/ingress-nginx` — affected >=0 <1.13.7
- Go: `k8s.io/ingress-nginx` — affected >=1.14.0 <1.14.3

## Details
A security issue was discovered in ingress-nginx where the validating admission controller feature is subject to a denial of service condition. By sending large requests to the validating admission controller, an attacker can cause memory consumption, which may result in the ingress-nginx controller pod being killed or the node running out of memory.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2026-24514
- https://github.com/kubernetes/kubernetes/issues/136680
- https://github.com/kubernetes/ingress-nginx
