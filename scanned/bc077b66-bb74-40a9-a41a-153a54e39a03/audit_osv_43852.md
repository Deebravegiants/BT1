# [C] MemOS Authentication Bypass via Unset INTERNAL_SERVICE_SECRET

## Summary
Severity: Critical
Advisory: CVE-2026-75110
CVSS: 9.0 (CVSS:4.0/AV:N/AC:L/AT:N/PR:N/UI:N/VC:H/VI:H/VA:H/SC:N/SI:N/SA:N)
Published: 2026-08-17
Source: https://osv.dev/vulnerability/CVE-2026-75110
Type: osv

## Details
MemOS is a memory operating system for LLMs and AI agents. In deployments where authentication is enabled (AUTH_ENABLED=true) but the undocumented, defaultless INTERNAL_SERVICE_SECRET environment variable is unset, the is_internal_request() check in src/memos/api/middleware/auth.py fails open: os.getenv("INTERNAL_SERVICE_SECRET") returns None and a request omitting the X-Internal-Service header also yields None, so the comparison None == None evaluates true. The request is then treated as a trusted internal principal and granted scopes: ["all"]. As a result, an unauthenticated remote attacker can reach the admin API-key management endpoints to mint API keys for any user, enumerate keys, revoke keys, and generate a master key for persistent privileged access, as well as all data endpoints.

## References
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/75xxx/CVE-2026-75110.json
- https://nvd.nist.gov/vuln/detail/CVE-2026-75110
- https://www.vulncheck.com/advisories/memos-authentication-bypass-via-unset-internal-service-secret
- https://github.com/MemTensor/MemOS/issues/2259
- https://github.com/MemTensor/MemOS
- https://github.com/MemTensor/MemOS/blob/main/src/memos/api/middleware/auth.py
