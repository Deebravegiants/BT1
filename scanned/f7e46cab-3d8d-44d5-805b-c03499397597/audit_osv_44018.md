# [H] Headroom Proxy Treats the Client-Supplied x-headroom-user-id Header as an Authenticated Identity

## Summary
Severity: High
Advisory: CVE-2026-77776
CVSS: 7.5 (CVSS:4.0/AV:N/AC:L/AT:N/PR:N/UI:N/VC:H/VI:H/VA:N/SC:N/SI:N/SA:N)
Published: 2026-08-21
Source: https://osv.dev/vulnerability/CVE-2026-77776
Type: osv

## Details
Headroom's LLM proxy derives the memory owner from the x-headroom-user-id request header. The header is read directly at several points in headroom/proxy/handlers/openai.py, including the chat completion and websocket paths, and nothing binds the value to the caller. A client can therefore name another user's identifier and read or write that user's stored LLM memory. The fix introduces a single resolve_memory_identity seam in headroom/proxy/identity.py that honors the header only for loopback or allowlisted callers and otherwise binds the identity to the proxy-token fingerprint or the operating system user. The pip console script binds 127.0.0.1 by default, but the reference docker-compose.yml ships --host 0.0.0.0 with published ports and no required HEADROOM_PROXY_TOKEN, which the server itself warns about at startup, so a deployment following the shipped compose exposes the affected data-plane routes to the network without authentication.

## References
- https://pypi.org
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/77xxx/CVE-2026-77776.json
- https://nvd.nist.gov/vuln/detail/CVE-2026-77776
- https://www.vulncheck.com/advisories/headroom-proxy-treats-the-client-supplied-x-headroom-user-id-header-as-an-authenticated-identity
- https://github.com/headroomlabs-ai/headroom/pull/2207
- https://github.com/headroomlabs-ai/headroom
- https://github.com/headroomlabs-ai/headroom/blob/v0.29.0/headroom/proxy/handlers/openai.py
- https://github.com/headroomlabs-ai/headroom/blob/v0.36.1/headroom/proxy/identity.py
