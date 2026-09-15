# [M] Kong Kubernetes Ingress Controller cluster-wide ingress configuration DoS via CA-certificate ID collision

## Summary
Severity: Medium
Advisory: CVE-2026-15228
Aliases: GHSA-g9h6-h2xj-mf78
CVSS: 6.0 (CVSS:4.0/AV:N/AC:L/AT:N/PR:L/UI:N/VC:N/VI:N/VA:H/SC:N/SI:N/SA:N)
Published: 2026-07-29
Source: https://osv.dev/vulnerability/CVE-2026-15228
Type: osv

## Details
Kong Kubernetes Ingress Controller (KIC) allows a user with namespace-scoped Secret creation privileges to cause a cluster-wide ingress configuration denial of service. KIC collects CA-certificate Secrets across all watched namespaces using a label selector alone, without ingress-class or namespace restrictions. The CA-certificate primary key is derived from a user-supplied field in the Secret. Duplicate CA-certificate IDs cause Kong Gateway to reject the entire configuration document and halting all ingress changes cluster-wide.

## References
- https://github.com
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/15xxx/CVE-2026-15228.json
- https://github.com/Kong/kubernetes-ingress-controller/security/advisories/GHSA-g9h6-h2xj-mf78
- https://nvd.nist.gov/vuln/detail/CVE-2026-15228
- https://github.com/Kong/kubernetes-ingress-controller
