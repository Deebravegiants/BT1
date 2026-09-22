# [C] Coolify Docker Compose Directive Injection in Application Deployment Workflow

## Summary
Severity: Critical
Advisory: CVE-2025-34159
CVSS: 9.0 (CVSS:4.0/AV:N/AC:L/AT:N/PR:L/UI:N/VC:H/VI:H/VA:H/SC:H/SI:H/SA:H)
Published: 2025-08-27
Source: https://osv.dev/vulnerability/CVE-2025-34159
Type: osv

## Details
Coolify versions prior to v4.0.0-beta.420.6 are vulnerable to a remote code execution vulnerability in the application deployment workflow. The platform allows authenticated users, with low-level member privileges, to inject arbitrary Docker Compose directives during project creation. By crafting a malicious service definition that mounts the host root filesystem, an attacker can gain full root access to the underlying server.

## References
- https://coolify.io/
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2025/34xxx/CVE-2025-34159.json
- https://nvd.nist.gov/vuln/detail/CVE-2025-34159
- https://github.com/coollabsio/coolify/releases/tag/v4.0.0-beta.420.7
- https://github.com/coollabsio/coolify
- https://github.com/Eyodav/CVE-2025-34159
