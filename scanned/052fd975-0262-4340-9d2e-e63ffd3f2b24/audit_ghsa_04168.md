# [H] Heimdall: IP Spoofing via Unvalidated Forwarding Headers

## Summary
Severity: High
Advisory: GHSA-38x9-25wx-7fg2
CVE: CVE-2026-57210
CWE: CWE-116, CWE-20, CWE-290
Ecosystem: Go
CVSS: CVSS:4.0/AV:N/AC:L/AT:P/PR:N/UI:N/VC:N/VI:N/VA:N/SC:H/SI:H/SA:N (CVSS_V4)
Published: 2026-06-18
Source: https://github.com/advisories/GHSA-38x9-25wx-7fg2
Type: github-advisory

## Affected
- Go: `https://github.com/dadrus/heimdall` — affected >=0 <0.17.17

## Details
### Summary

When the `trusted_proxies` option is configured, heimdall extracts client IP addresses from the `Forwarded` (`for=` parameter) and `X-Forwarded-For` headers and exposes them as `Request.ClientIPAddresses` to the rule pipeline. However, extracted values are not validated to be syntactically valid IP addresses. Arbitrary strings, malformed IP literals, and RFC 7239 `unknown` values and obfuscated identifiers are accepted without further checks.
In addition, the `Forwarded` header parser splits on `,` and `;` without accounting for RFC 7239 quoted strings, which can cause a single quoted value to be parsed as multiple entries, with fragments — including trailing quote characters — treated as independent addresses.

### Impact

`Request.ClientIPAddresses` is available to all pipeline mechanisms. Its contents can therefore influence rule evaluation in deployments where rules reference this property — for example, in a `CEL` authorizer that checks whether a request originates from a trusted IP range using the `networks()` function, or in a `Remote` authorizer that forwards the client IP as part of its payload to an external authorization system. Whether and how `Request.ClientIPAddresses` is used is entirely determined by the rule configuration.

Additionally, in proxy mode, `Request.ClientIPAddresses` is used directly to construct the `X-Forwarded-For` and `Forwarded` headers forwarded to upstream services. Injected or malformed values are therefore propagated to upstream services unchanged.

### Attack Scenarios

All scenarios require that `trusted_proxies` is configured. If this option is not set, heimdall ignores forwarding headers entirely, and this vulnerability is not exploitable. Scenarios A and C  (see below) additionally require that rules reference `Request.ClientIPAddresses` in their pipeline.

#### Scenario A – Manipulation of rule evaluation

An attacker who can influence forwarding headers — either by connecting directly to heimdall or through a proxy that does not sanitize these headers — can inject arbitrary values into `Request.ClientIPAddresses`. In deployments where a rule references this property (e.g. to restrict access to specific IP ranges), this may allow an attacker to bypass the intended access control logic.

#### Scenario B – IP spoofing against upstream services (proxy mode)

In proxy mode, injected or malformed values in `Request.ClientIPAddresses` are written unchanged into the `X-Forwarded-For` header sent to upstream services. Upstream services that trust this header may therefore receive and act on attacker-controlled IP values.

#### Scenario C – Malformed entries via quoted-string misparse

A `Forwarded` header containing a quoted value with embedded delimiters (`,` or `;`) is misparsed, producing unintended additional entries in `Request.ClientIPAddresses`, including malformed fragments with trailing quote characters.

### Workarounds

* Ensure at the network level that only trusted proxies can communicate directly with heimdall.
* Ensure that the proxy forwarding the requests to heimdall sanitizes or overrides (not merely appends to) `Forwarded` or `X-Forwarded-For` headers before forwarding them.
* Avoid relying on `Request.ClientIPAddresses` for security-sensitive decisions until patched

## References
- https://github.com/dadrus/heimdall/security/advisories/GHSA-38x9-25wx-7fg2
- https://github.com/dadrus/heimdall
