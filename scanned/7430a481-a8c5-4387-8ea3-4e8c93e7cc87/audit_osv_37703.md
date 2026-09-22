# [H] ingress-nginx rewrite-target nginx configuration injection

## Summary
Severity: High
Advisory: CVE-2026-3288
CVSS: 8.8 (CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H)
Published: 2026-03-09
Source: https://osv.dev/vulnerability/CVE-2026-3288
Type: osv

## Details
A security issue was discovered in ingress-nginx where the `nginx.ingress.kubernetes.io/rewrite-target` Ingress annotation can be used to inject configuration into nginx. This can lead to arbitrary code execution in the context of the ingress-nginx controller, and disclosure of Secrets accessible to the controller. (Note that in the default installation, the controller can access all Secrets cluster-wide.)

## References
- http://www.openwall.com/lists/oss-security/2026/03/09/8
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/3xxx/CVE-2026-3288.json
- https://nvd.nist.gov/vuln/detail/CVE-2026-3288
- https://github.com/kubernetes/kubernetes/issues/137560
- https://github.com/kubernetes/ingress-nginx
- https://github.com/bvabhishek/CVE-2026-3288-lab
