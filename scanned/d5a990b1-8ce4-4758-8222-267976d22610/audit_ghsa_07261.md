# [H] Tesla vulnerable to atom exhaustion via untrusted URL scheme

## Summary
Severity: High
Advisory: GHSA-h74c-q9j7-mpcm
CVE: CVE-2026-48597
CWE: CWE-770
Ecosystem: Hex
CVSS: CVSS:4.0/AV:N/AC:L/AT:P/PR:N/UI:N/VC:N/VI:N/VA:H/SC:N/SI:N/SA:N (CVSS_V4)
Published: 2026-07-10
Source: https://github.com/advisories/GHSA-h74c-q9j7-mpcm
Type: github-advisory

## Affected
- Hex: `tesla` — affected >=1.3.0 <1.18.3

## Details
### Summary

In the Mint adapter for the Tesla HTTP client library, `Tesla.Adapter.Mint.open_conn/2` passes the URL scheme of every outgoing request through `String.to_atom/1` with no allow-list validation. Because BEAM atoms are permanent (never garbage-collected) and the atom table is bounded at roughly 1,048,576 entries, an attacker who can vary the URL scheme across requests can mint one fresh atom per request and eventually exhaust the table, crashing the VM.

### Details

**Vulnerable call** (`lib/tesla/adapter/mint.ex`, `open_conn/2`): the scheme field parsed from the request URI is passed directly to `String.to_atom/1` before being forwarded to `Mint.HTTP.connect/4`. Even though `Mint` raises for unrecognised schemes, the atom is already interned by that point. The function's HTTPS-branch guard confirms that no scheme normalisation occurs beforehand.

The attack surface has two entry points. First, any application-level URL-forwarding feature (webhook relay, link preview, SSRF-style proxy) where untrusted input reaches `Tesla.get/2` or equivalent. Second, any pipeline that includes `Tesla.Middleware.FollowRedirects`: a server under the attacker's control can return a `Location` header with a novel scheme, triggering the atom creation on the redirect follow.

### PoC

1. Stand up any application that accepts a user-supplied URL and forwards it through `Tesla.Adapter.Mint`.
2. Send requests to the application, each with a distinct, previously unseen URL scheme (e.g. `atk1://`, `atk2://`, ...).
3. Each request interns one new permanent atom; `Mint` rejects the connection but the atom persists.
4. After approximately 1,000,000 requests the BEAM atom table is exhausted and the VM crashes.

### Impact

High severity (CVSS v4.0: 8.2). Any application using `tesla` 1.3.0 through 1.18.2 with `Tesla.Adapter.Mint` that allows untrusted input to influence request URLs is vulnerable to remote denial of service. No authentication or special privileges are required beyond access to the application's HTTP endpoint. Fixed in tesla 1.18.3.

### Configurations

The application must use `Tesla.Adapter.Mint` and either expose a feature that forwards attacker-controlled URLs to Tesla, or include `Tesla.Middleware.FollowRedirects` in the middleware pipeline.

### References

* Introduction commit: https://github.com/elixir-tesla/tesla/commit/ccd0823d4ba37581a37d8f6108f9a81b263237ef
* Patch commit: https://github.com/elixir-tesla/tesla/commit/4699c3cb3e2fd6078f99f45f11cf7466aeedbf0e

## References
- https://github.com/elixir-tesla/tesla/security/advisories/GHSA-h74c-q9j7-mpcm
- https://nvd.nist.gov/vuln/detail/CVE-2026-48597
- https://github.com/elixir-tesla/tesla/commit/4699c3cb3e2fd6078f99f45f11cf7466aeedbf0e
- https://cna.erlef.org/cves/CVE-2026-48597.html
- https://github.com/elixir-tesla/tesla
- https://osv.dev/vulnerability/EEF-CVE-2026-48597
