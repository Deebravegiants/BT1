# [M] Kubernetes - API server - Aggregated API server can cause clients to be redirected (SSRF)

## Summary
Severity: Medium
Advisory: CVE-2022-3172
CVSS: 5.1 (CVSS:3.1/AV:N/AC:H/PR:H/UI:R/S:C/C:L/I:L/A:L)
Published: 2023-11-03
Source: https://osv.dev/vulnerability/CVE-2022-3172
Type: osv

## Details
A security issue was discovered in kube-apiserver that allows an 
aggregated API server to redirect client traffic to any URL.  This could
 lead to the client performing unexpected actions as well as forwarding 
the client's API server credentials to third parties.

## References
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2022/3xxx/CVE-2022-3172.json
- https://nvd.nist.gov/vuln/detail/CVE-2022-3172
- https://security.netapp.com/advisory/ntap-20231221-0005/
- https://github.com/kubernetes/kubernetes/issues/112513
- https://github.com/kubernetes/kubernetes
- https://groups.google.com/g/kubernetes-security-announce/c/_aLzYMpPRak
