# [C] txtai - Unauthenticated Remote Code Execution via Unsafe Reflection in API /reindex function Parameter

## Summary
Severity: Critical
Advisory: CVE-2026-58449
CVSS: 9.0 (CVSS:4.0/AV:N/AC:L/AT:N/PR:N/UI:N/VC:H/VI:H/VA:H/SC:N/SI:N/SA:N)
Published: 2026-06-30
Source: https://osv.dev/vulnerability/CVE-2026-58449
Type: osv

## Details
txtai through 9.10.0, fixed in commit 11b32da, exposes an API /reindex endpoint whose function body parameter is resolved through txtai.util.Resolver, which performs __import__ and getattr on the caller-supplied dotted path with no allowlist. When the API is exposed with no TOKEN configured (authentication is opt-in, so all endpoints are unauthenticated) and the index is configured writable, a remote attacker can set function to an arbitrary callable such as subprocess.getoutput, achieving remote code execution as the server process during reindexing. Exploitation requires those deployment conditions (API exposed, no TOKEN, writable index); it is not the default configuration. The fix gates the endpoint behind a new reindex configuration flag.

## References
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/58xxx/CVE-2026-58449.json
- https://nvd.nist.gov/vuln/detail/CVE-2026-58449
- https://www.vulncheck.com/advisories/txtai-unauthenticated-remote-code-execution-via-unsafe-reflection-in-api-reindex-function-parameter
- https://github.com/neuml/txtai/issues/1111
- https://github.com/neuml/txtai/issues/1122
- https://github.com/neuml/txtai/commit/11b32da720f03276199ebc5583c15fc5d1ccafd3
- https://github.com/neuml/txtai
