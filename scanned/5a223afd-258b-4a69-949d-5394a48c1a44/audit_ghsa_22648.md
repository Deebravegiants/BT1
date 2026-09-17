# [M] Kubernetes DoS Vulnerability

## Summary
Severity: Medium
Advisory: GHSA-q4rr-64r9-fwgf
CVE: CVE-2019-1002100
CWE: CWE-770
Ecosystem: Go
CVSS: CVSS:3.0/AV:N/AC:L/PR:L/UI:N/S:U/C:N/I:N/A:H (CVSS_V3)
Published: 2022-05-13
Source: https://github.com/advisories/GHSA-q4rr-64r9-fwgf
Type: github-advisory

## Affected
- Go: `k8s.io/kubernetes` — affected >=1.0.0
- Go: `k8s.io/kubernetes` — affected >=1.11.0 <1.11.8
- Go: `k8s.io/kubernetes` — affected >=1.12.0 <1.12.6
- Go: `k8s.io/kubernetes` — affected >=1.13.0 <1.13.4

## Details
In all Kubernetes versions prior to v1.11.8, v1.12.6, and v1.13.4, users that are authorized to make patch requests to the Kubernetes API Server can send a specially crafted patch of type "json-patch" (e.g. `kubectl patch --type json` or `"Content-Type: application/json-patch+json"`) that consumes excessive resources while processing, causing a Denial of Service on the API Server.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2019-1002100
- https://github.com/kubernetes/kubernetes/issues/74534
- https://access.redhat.com/errata/RHSA-2019:1851
- https://access.redhat.com/errata/RHSA-2019:3239
- https://github.com/kubernetes/kubernetes
- https://groups.google.com/forum/#!topic/kubernetes-announce/vmUUNkYfG9g
- https://security.netapp.com/advisory/ntap-20190416-0002
- https://web.archive.org/web/20210125011246/https://www.securityfocus.com/bid/107290
