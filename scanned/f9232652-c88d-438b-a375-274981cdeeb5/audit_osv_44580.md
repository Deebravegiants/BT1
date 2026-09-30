# [C] Coolify before 4.2.0 Remote Code Execution via Environment Variable Key

## Summary
Severity: Critical
Advisory: CVE-2026-84694
CVSS: 9.0 (CVSS:4.0/AV:N/AC:L/AT:N/PR:L/UI:N/VC:H/VI:H/VA:H/SC:N/SI:N/SA:N)
Published: 2026-09-02
Source: https://osv.dev/vulnerability/CVE-2026-84694
Type: osv

## Details
Coolify before 4.2.0 fails to properly escape environment variable key names in Docker commands executed over SSH on managed servers. Authenticated attackers can inject shell metacharacters into environment variable keys to execute arbitrary commands on the server host outside containers.

## References
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/84xxx/CVE-2026-84694.json
- https://github.com/coollabsio/coolify/releases/tag/v4.2.0
- https://nvd.nist.gov/vuln/detail/CVE-2026-84694
- https://www.vulncheck.com/advisories/coolify-before-4.2.0-remote-code-execution-via-environment-variable-key
- https://github.com/coollabsio/coolify/commit/b50839d4515b115b7ded5db609471440249995da
- https://github.com/coollabsio/coolify
- https://github.com/coollabsio/coolify/blob/v4.1.2/app/Policies/ApplicationPolicy.php
- https://github.com/coollabsio/coolify/blob/v4.1.2/app/Support/ValidationPatterns.php
