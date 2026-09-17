# [C] Jupyter Enterprise Gateway: Jinja2 Template Server Side Template Injection results in Remote Code Execution

## Summary
Severity: Critical
Advisory: CVE-2026-44181
Aliases: GHSA-f49j-v924-fx9w, PYSEC-2026-364
CVSS: 9.0 (CVSS:4.0/AV:N/AC:L/AT:N/PR:N/UI:N/VC:H/VI:H/VA:H/SC:H/SI:H/SA:H)
Published: 2026-07-16
Source: https://osv.dev/vulnerability/CVE-2026-44181
Type: osv

## Details
Jupyter Enterprise Gateway launches remote Jupyter Notebook kernels across distributed clusters like Apache Spark, Kubernetes, and Docker Swarm. In versions 2.0.0rc2 and above, prior to 3.3.0, the environment variables (KERNEL_XXX) used during the rendering of the Kubernetes manifest are vulnerable to Server Side Template Injection (SSTI). By including Jinja2 template expressions it is possible to execution Python code and OS Commands in the Enterprise Gateway service. The code can use or steal the Kubernetes service account token, which can steal Kubernetes secrets and be used to fully compromise the Kubernetes cluster by scheduling a privileged pod or a pod with a hostPath volume mount. This issue has been fixed in version 3.3.0.

## References
- https://github.com/jupyter-server/enterprise_gateway/releases/tag/v3.3.0
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/44xxx/CVE-2026-44181.json
- https://github.com/jupyter-server/enterprise_gateway/security/advisories/GHSA-f49j-v924-fx9w
- https://nvd.nist.gov/vuln/detail/CVE-2026-44181
