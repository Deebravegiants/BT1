# [H] CVE-2021-25746

## Summary
Severity: High
Advisory: CVE-2021-25746
CVSS: 7.1 (CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:H/I:L/A:N)
Published: 2022-05-06
Source: https://osv.dev/vulnerability/CVE-2021-25746
Type: osv

## Details
A security issue was discovered in ingress-nginx where a user that can create or update ingress objects can use .metadata.annotations in an Ingress object (in the networking.k8s.io or extensions API group) to obtain the credentials of the ingress-nginx controller. In the default configuration, that credential has access to all secrets in the cluster.

## References
- https://security.netapp.com/advisory/ntap-20220609-0006/
- https://github.com/kubernetes/ingress-nginx/issues/8503
- https://groups.google.com/g/kubernetes-security-announce/c/hv2-SfdqcfQ
