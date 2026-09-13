# [M] nono-py vulnerable to authorization bypass / policy confusion

## Summary
Severity: Medium
Advisory: GHSA-9j7f-3r4p-pwh6
CWE: CWE-1188
Ecosystem: PyPI
CVSS: CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:C/C:L/I:L/A:N (CVSS_V3)
Published: 2026-06-26
Source: https://github.com/advisories/GHSA-9j7f-3r4p-pwh6
Type: github-advisory

## Affected
- PyPI: `nono-py` — affected >=0 <0.11.0

## Details
The python API made a restrictive-looking configuration unsafe by default. A caller could configure only reverse-
proxy credential routes, put the child in CapabilitySet.proxy_only, and reasonably expect network access to be limited
to those routes. Instead, because empty allowed_hosts meant allow-all inside nono-proxy, the child could use the local
proxy as a transparent CONNECT tunnel to non-route nominated hosts (not including metadata endpoints).

That is an authorization bypass / policy confusion issue:

- Intended policy: route-only proxy access.
- Actual policy: route-only plus arbitrary transparent CONNECT.
- Boundary crossed: sandboxed child gains broader outbound network reach than the Python policy appears to grant.
- Impact depends on environment, but it can allow exfiltration or access to unintended internet/internal services
  through the unsandboxed proxy.

This should be classified as medium severity by default, potentially high if users rely on route-only configs for strict egress
control around untrusted code or sensitive credentials. The fix is security-relevant because it changes the default from
implicit allow-all to explicit opt-in.

## References
- https://github.com/always-further/nono-py/security/advisories/GHSA-9j7f-3r4p-pwh6
- https://github.com/nolabs-ai/nono-py/commit/163fca083a189967b882d1005bfba099fc9a9d63
- https://github.com/always-further/nono-py
