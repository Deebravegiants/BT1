# [C] Budibase before 3.41.3 Remote Code Execution via Plugin eval()

## Summary
Severity: Critical
Advisory: CVE-2026-82244
Aliases: GHSA-gwr2-pgg3-p7xp
CVSS: 9.0 (CVSS:4.0/AV:N/AC:L/AT:N/PR:H/UI:N/VC:H/VI:H/VA:H/SC:H/SI:H/SA:H)
Published: 2026-08-28
Source: https://osv.dev/vulnerability/CVE-2026-82244
Type: osv

## Details
Budibase versions before 3.41.3 contain a remote code execution vulnerability in plugin handling that allows authenticated admin users to execute arbitrary code by uploading a malicious plugin tarball. The server calls eval() on plugin JavaScript files without sandboxing in the main Node.js process, enabling attackers to exfiltrate environment variables and credentials with root privileges in default deployments.

## References
- https://github.com/Budibase/budibase/security/advisories/GHSA-gwr2-pgg3-p7xp
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/82xxx/CVE-2026-82244.json
- https://nvd.nist.gov/vuln/detail/CVE-2026-82244
- https://www.vulncheck.com/advisories/budibase-before-3.41.3-remote-code-execution-via-plugin-eval
