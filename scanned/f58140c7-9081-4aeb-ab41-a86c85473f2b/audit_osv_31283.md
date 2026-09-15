# [H] CVE-2024-7646

## Summary
Severity: High
Advisory: CVE-2024-7646
Aliases: GO-2024-3075
CVSS: 8.8 (CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H)
Published: 2024-08-16
Source: https://osv.dev/vulnerability/CVE-2024-7646
Type: osv

## Details
A security issue was discovered in ingress-nginx where an actor with permission to create Ingress objects (in the `networking.k8s.io` or `extensions` API group) can bypass annotation validation to inject arbitrary commands and obtain the credentials of the ingress-nginx controller. In the default configuration, that credential has access to all secrets in the cluster.

## References
- http://www.openwall.com/lists/oss-security/2024/08/16/5
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2024/7xxx/CVE-2024-7646.json
- https://nvd.nist.gov/vuln/detail/CVE-2024-7646
- https://github.com/kubernetes/kubernetes/issues/126744
- https://github.com/kubernetes/ingress-nginx/pull/11719
- https://github.com/kubernetes/ingress-nginx/pull/11721
- https://groups.google.com/g/kubernetes-security-announce/c/a1__cKjWkfA
