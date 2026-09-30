# [H] Kubernetes - Windows nodes - Insufficient input sanitization leads to privilege escalation

## Summary
Severity: High
Advisory: CVE-2023-3955
Aliases: GHSA-q78c-gwqw-jcmc, GO-2023-2170
CVSS: 8.8 (CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H)
Published: 2023-10-31
Source: https://osv.dev/vulnerability/CVE-2023-3955
Type: osv

## Details
A security issue was discovered in Kubernetes where a user
 that can create pods on Windows nodes may be able to escalate to admin 
privileges on those nodes. Kubernetes clusters are only affected if they
 include Windows nodes.

## References
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2023/3xxx/CVE-2023-3955.json
- https://nvd.nist.gov/vuln/detail/CVE-2023-3955
- https://security.netapp.com/advisory/ntap-20231221-0002/
- https://github.com/kubernetes/kubernetes/issues/119595
- https://github.com/kubernetes/kubernetes
- https://groups.google.com/g/kubernetes-security-announce/c/JrX4bb7d83E
