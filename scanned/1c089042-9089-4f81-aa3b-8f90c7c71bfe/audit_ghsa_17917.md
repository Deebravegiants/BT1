# [H] @musistudio/claude-code-router has improper CORS configuration

## Summary
Severity: High
Advisory: GHSA-8hmm-4crw-vm2c
CVE: CVE-2025-57755
CWE: CWE-200, CWE-942
Ecosystem: npm
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:N (CVSS_V3)
Published: 2025-08-21
Source: https://github.com/advisories/GHSA-8hmm-4crw-vm2c
Type: github-advisory

## Affected
- npm: `@musistudio/claude-code-router` — affected >=0 <1.0.34

## Details
### Impact
Due to improper Cross-Origin Resource Sharing (CORS) configuration, there is a risk that user API Keys or equivalent credentials may be exposed to untrusted domains. Attackers could exploit this misconfiguration to steal credentials, abuse accounts, exhaust quotas, or access sensitive data.

### Patches
The issue has been patched in v1.0.34.

## References
- https://github.com/musistudio/claude-code-router/security/advisories/GHSA-8hmm-4crw-vm2c
- https://nvd.nist.gov/vuln/detail/CVE-2025-57755
- https://github.com/musistudio/claude-code-router/issues/549
- https://github.com/musistudio/claude-code-router
