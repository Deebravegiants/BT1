# [H] CVE-2021-25742

## Summary
Severity: High
Advisory: CVE-2021-25742
CVSS: 7.1 (CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:H/I:L/A:N)
Published: 2021-10-29
Source: https://osv.dev/vulnerability/CVE-2021-25742
Type: osv

## Details
A security issue was discovered in ingress-nginx where a user that can create or update ingress objects can use the custom snippets feature to obtain all secrets in the cluster.

## References
- https://groups.google.com/g/kubernetes-security-announce/c/mT4JJxi9tQY
- https://security.netapp.com/advisory/ntap-20211203-0001/
- https://github.com/kubernetes/ingress-nginx/issues/7837
