# [C] LiteLLM: Authentication Bypass via Host Header Injection

## Summary
Severity: Critical
Advisory: GHSA-4xpc-pv4p-pm3w
CVE: CVE-2026-49468
CWE: CWE-290
Ecosystem: PyPI
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H (CVSS_V3)
Published: 2026-06-16
Source: https://github.com/advisories/GHSA-4xpc-pv4p-pm3w
Type: github-advisory

## Affected
- PyPI: `litellm` — affected >=0 <1.84.0

## Details
### Impact

A Host-header parsing flaw in the LiteLLM proxy could, under specific conditions, allow unauthenticated access to protected management routes.

The auth layer derived the effective route from `request.url.path` in `litellm/proxy/auth/auth_utils.py::get_request_route()`, which Starlette reconstructs from the `Host` header. A crafted `Host` could therefore make the auth gate evaluate a different route from the one FastAPI dispatched.

**Most deployments are not affected.** The bypass is blocked by any upstream layer that validates or normalizes `Host`, such as:

- a CDN or WAF, such as Cloudflare
- a reverse proxy with `server_name` allowlists
- a host-based load balancer

**LiteLLM Cloud customers are not affected.**

### Patches

Fixed in **`1.84.0`**. Upgrade to `1.84.0` or later. No configuration change is required.

### Workarounds

If upgrading is not immediately possible, place the proxy behind an upstream component that validates or normalizes the `Host` header before forwarding (a CDN/WAF, a reverse proxy with explicit `server_name` allowlists, or a cloud load balancer with host-based routing rules), or otherwise restrict network access to the proxy listener.

### References

- Patched release: [`v1.84.0`](https://github.com/BerriAI/litellm/releases/tag/v1.84.0)

**Discovery Credit**: Le The Thang (KCSC) and Kim Ngoc Chung (One Mount Group)

## References
- https://github.com/BerriAI/litellm/security/advisories/GHSA-4xpc-pv4p-pm3w
- https://nvd.nist.gov/vuln/detail/CVE-2026-49468
- https://access.redhat.com/security/cve/CVE-2026-49468
- https://bugzilla.redhat.com/show_bug.cgi?id=2491520
- https://github.com/BerriAI/litellm
- https://github.com/BerriAI/litellm/releases/tag/v1.84.0
- https://github.com/advisories/GHSA-4xpc-pv4p-pm3w
- https://github.com/pypa/advisory-database/tree/main/vulns/litellm/PYSEC-2026-388.yaml
- https://pypi.org/project/litellm
- https://security.access.redhat.com/data/csaf/v2/vex/2026/cve-2026-49468.json
