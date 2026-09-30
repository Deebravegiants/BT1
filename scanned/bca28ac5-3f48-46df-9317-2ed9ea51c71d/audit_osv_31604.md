# [H] ingress-nginx auth-proxy-set-headers nginx configuration injection

## Summary
Severity: High
Advisory: CVE-2025-15566
CVSS: 8.8 (CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H)
Published: 2026-02-06
Source: https://osv.dev/vulnerability/CVE-2025-15566
Type: osv

## Details
A security issue was discovered in ingress-nginx where the `nginx.ingress.kubernetes.io/auth-proxy-set-headers` Ingress annotation can be used to inject configuration into nginx. This can lead to arbitrary code execution in the context of the ingress-nginx controller, and disclosure of Secrets accessible to the controller. (Note that in the default installation, the controller can access all Secrets cluster-wide.)

## References
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2025/15xxx/CVE-2025-15566.json
- https://nvd.nist.gov/vuln/detail/CVE-2025-15566
- https://github.com/kubernetes/kubernetes/issues/136789
- https://github.com/kubernetes/ingress-nginx
