# [M] Insecure default setting for Server Pro installed via Overleaf toolkit

## Summary
Severity: Medium
Advisory: CVE-2024-45313
Aliases: GHSA-m95q-g8qg-wgj4
CVSS: 5.4 (CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:L/I:L/A:N)
Published: 2024-09-02
Source: https://osv.dev/vulnerability/CVE-2024-45313
Type: osv

## Details
Overleaf is a web-based collaborative LaTeX editor. When installing Server Pro using the Overleaf Toolkit from before 2024-07-17 or legacy docker-compose.yml from before 2024-08-28, the configuration for LaTeX compiles was insecure by default, requiring the administrator to enable the security features via a configuration setting (`SIBLING_CONTAINERS_ENABLED` in Toolkit, `SANDBOXED_COMPILES` in legacy docker-compose/custom deployments). If these security features are not enabled then users have access to the `sharelatex` container resources (filesystem, network, environment variables) when running compiles, leading to multiple file access vulnerabilities, either directly or via symlinks created during compiles. The setting has now been changed to be secure by default for new installs in the Toolkit and legacy docker-compose deployment. The Overleaf Toolkit has been updated to set `SIBLING_CONTAINERS_ENABLED=true` by default for new installs. It is recommended that any existing installations using the previous default setting migrate to using sibling containers. Existing installations can set `SIBLING_CONTAINERS_ENABLED=true` in `config/overleaf.rc` as a mitigation. In legacy docker-compose/custom deployments `SANDBOXED_COMPILES=true` should be used.

## References
- https://github.com/overleaf/overleaf/wiki/Server-Pro:-Sandboxed-Compiles
- https://github.com/overleaf/toolkit/blob/master/doc/sandboxed-compiles.md#enabling-sibling-containers
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2024/45xxx/CVE-2024-45313.json
- https://github.com/overleaf/overleaf/security/advisories/GHSA-m95q-g8qg-wgj4
- https://nvd.nist.gov/vuln/detail/CVE-2024-45313
- https://github.com/overleaf/toolkit/commit/7a8401897b24777b47338452ff8d12e2fb6dd5ff
