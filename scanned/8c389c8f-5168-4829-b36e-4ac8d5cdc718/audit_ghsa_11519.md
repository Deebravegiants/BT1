# [H] elixir-nodejs has Cross-User Data Leakage or Information Disclosure due to Worker Protocol Race Condition

## Summary
Severity: High
Advisory: GHSA-rwcr-rpcc-3g9m
CVE: CVE-2026-33872
CWE: CWE-362
Ecosystem: Hex
CVSS: CVSS:4.0/AV:N/AC:L/AT:N/PR:L/UI:N/VC:H/VI:N/VA:N/SC:N/SI:N/SA:N (CVSS_V4)
Published: 2026-03-26
Source: https://github.com/advisories/GHSA-rwcr-rpcc-3g9m
Type: github-advisory

## Affected
- Hex: `nodejs` — affected >=0 <3.1.4

## Details
### Impact

This vulnerability results in Cross-User Data Leakage or Information Disclosure due to a race condition in the worker protocol.

The lack of request-response correlation creates a "stale response" vulnerability. Because the worker does not verify which request a response belongs to, it may return the next available data in the buffer to an unrelated caller.

In high-throughput environments where the library processes sensitive user data (e.g., PII, authentication tokens, or private records), a timeout or high concurrent load can cause Data A (belonging to User A) to be returned to User B.

This may lead to unauthorized information disclosure that is difficult to trace, as the application may not throw an error but instead provide "valid-looking" yet entirely incorrect and private data to the wrong session.

### Patches

fixed in v3.1.4

### Resources
https://github.com/revelrylabs/elixir-nodejs/issues/100

https://github.com/revelrylabs/elixir-nodejs/pull/105

## References
- https://github.com/revelrylabs/elixir-nodejs/security/advisories/GHSA-rwcr-rpcc-3g9m
- https://nvd.nist.gov/vuln/detail/CVE-2026-33872
- https://github.com/revelrylabs/elixir-nodejs/issues/100
- https://github.com/revelrylabs/elixir-nodejs/pull/105
- https://github.com/revelrylabs/elixir-nodejs
- https://github.com/revelrylabs/elixir-nodejs/releases/tag/v3.1.4
