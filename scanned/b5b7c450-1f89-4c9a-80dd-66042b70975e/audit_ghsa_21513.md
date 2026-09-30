# [C] KubeView vulnerable to full cluster takeover due to improper authentication

## Summary
Severity: Critical
Advisory: GHSA-22vc-5pgw-644q
CVE: CVE-2022-45933
CWE: CWE-287, CWE-306
Ecosystem: Go
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H (CVSS_V3)
Published: 2022-11-27
Source: https://github.com/advisories/GHSA-22vc-5pgw-644q
Type: github-advisory

## Affected
- Go: `github.com/benc-uk/kubeview` — affected >=0

## Details
KubeView through 0.1.31 allows attackers to obtain control of a Kubernetes cluster because api/scrape/kube-system does not require authentication, and retrieves certificate files that can be used for authentication as kube-admin. NOTE: the vendor's position is that KubeView was a "fun side project and a learning exercise," and not "very secure."

## References
- https://nvd.nist.gov/vuln/detail/CVE-2022-45933
- https://github.com/benc-uk/kubeview/issues/95
- https://github.com/benc-uk/kubeview
