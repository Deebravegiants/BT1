# [C] Signal K Server Vulnerable to Remote Code Execution via Malicious npm Package

## Summary
Severity: Critical
Advisory: CVE-2025-68619
Aliases: GHSA-93jc-vqqc-vvvh
CVSS: 9.0 (CVSS:4.0/AV:N/AC:L/AT:N/PR:H/UI:N/VC:H/VI:H/VA:H/SC:N/SI:N/SA:N/E:P)
Published: 2026-01-01
Source: https://osv.dev/vulnerability/CVE-2025-68619
Type: osv

## Details
Signal K Server is a server application that runs on a central hub in a boat. Versions prior to 2.19.0 of the appstore interface allow administrators to install npm packages through a REST API endpoint. While the endpoint validates that the package name exists in the npm registry as a known plugin or webapp, the version parameter accepts arbitrary npm version specifiers including URLs. npm supports installing packages from git repositories, GitHub shorthand syntax, and HTTP/HTTPS URLs pointing to tarballs. When npm installs a package, it can automatically execute any `postinstall` script defined in `package.json`, enabling arbitrary code execution. The vulnerability exists because npm's version specifier syntax is extremely flexible, and the SignalK code passes the version parameter directly to npm without sanitization. An attacker with admin access can install a package from an attacker-controlled source containing a malicious `postinstall` script. Version 2.19.0 contains a patch for the issue.

## References
- https://github.com/SignalK/signalk-server/releases/tag/v2.19.0
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2025/68xxx/CVE-2025-68619.json
- https://github.com/SignalK/signalk-server/security/advisories/GHSA-93jc-vqqc-vvvh
- https://nvd.nist.gov/vuln/detail/CVE-2025-68619
