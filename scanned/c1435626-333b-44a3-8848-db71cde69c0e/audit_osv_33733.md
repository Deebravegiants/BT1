# [M] Portainer HTTP Headers May Leak to Malicious Container Registries

## Summary
Severity: Medium
Advisory: CVE-2025-49593
Aliases: GHSA-h5jw-8c32-xfv6
CVSS: 6.8 (CVSS:3.1/AV:N/AC:L/PR:H/UI:R/S:U/C:H/I:H/A:H)
Published: 2025-06-17
Source: https://osv.dev/vulnerability/CVE-2025-49593
Type: osv

## Details
Portainer Community Edition is a lightweight service delivery platform for containerized applications that can be used to manage Docker, Swarm, Kubernetes and ACI environments. Prior to STS version 2.31.0 and LTS version 2.27.7, if a Portainer administrator can be convinced to register a malicious container registry, or an existing container registry can be taken over, HTTP Headers (including registry authentication credentials or Portainer session tokens) may be leaked to that registry. This issue has been patched in STS version 2.31.0 and LTS version 2.27.7.

## References
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2025/49xxx/CVE-2025-49593.json
- https://github.com/portainer/portainer/security/advisories/GHSA-h5jw-8c32-xfv6
- https://nvd.nist.gov/vuln/detail/CVE-2025-49593
- https://github.com/portainer/portainer/commit/384cb53c64af78af8e1ac7ef5b0f91bad530e989
- https://github.com/portainer/portainer/commit/b767dcb27ed253b423facd2e04ef971985950fd3
