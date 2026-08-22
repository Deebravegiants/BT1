# [M] web3.py: SSRF via CCIP Read (EIP-3668) OffchainLookup URL handling

## Summary
Severity: Medium
Chain: Tooling
Component: web3
CVE: CVE-2026-40072
CWE: Server-Side Request Forgery (SSRF)
Published: 2026-04-04
Source: https://github.com/advisories/GHSA-5hr4-253g-cpx2
Type: github-advisory

## Details
## Summary

web3.py implements CCIP Read / `OffchainLookup` (EIP-3668) by performing HTTP requests to URLs supplied by smart contracts in `offchain_lookup_payload["urls"]`. The implementation uses these contract-supplied URLs directly (after `{sender}` / `{data}` template substitution) without any destination validation:

- No restriction to `https://` (and no opt-in gate for `http://`)
- No hostname or IP allowlist
- No blocking of private/reserved IP ranges (loopback, link-local, RFC1918)
- No redirect target validation (both `requests` and `aiohttp` follow redirects by default)

**CCIP Read is enabled by default** (`global_ccip_read_enabled = True` on all providers), meaning any application using web3.py's `.call()` method is exposed without explicit opt-in.

This results in **Server-Side Request Forgery (SSRF)** when web3.py is used in backend services, indexers, APIs, or any environment that performs `eth_call` / `.call()` against untrusted or user-supplied contract addresses. A malicious contract can force the web3.py process to issue HTTP requests to arbitrary destinations, including internal network services and cloud metadata endpoints.

---

## Why This Is a Vulnerability

The argument is not that CCIP Read itself is invalid or that web3.py should stop supporting EIP-3668. The issue is that, in server-side deployments (backends, indexers, bots, APIs), the current implementation doesn't provide destination policy controls, such as a validation/override hook, private-range blocking, or redirect target checks, which means contract controlled CCIP URLs can be used as an SSRF primitive.

This is consistent with EIP-3668's own security considerations, which recommends that client libraries "provide clients with a hook to override CCIP read calls, either by rewriting them to use a proxy service, or by denying them entirely" and that "this mechanism or another should be written so as to easily facilitate adding domains to allowlists or blocklists." The mitigations I'm suggesting are meant to align with that guidance without breaking CCIP Read support.

- **Default-on exposure.** CCIP Read is enabled by default on all web3.py providers (`global_ccip_read_enabled = True`). Users who never intend to use CCIP Read, and who may not even know the feature exists, are silently exposed. A feature that makes unsanitized outbound requests to attacker-controlled URLs should not be enabled by default without safety guardrails.

- **Library vs. application responsibility.** web3.py is a widely-used library. Expecting every downstream application to independently implement SSRF protections around `.call()` is unreasonable, especially for a feature that fires automatically and invisibly on a specific revert pattern. Safe defaults at the library level are the standard expectation for any library that issues outbound HTTP requests to externally-controlled URLs.

---

## Affected Code

### Sync CCIP handler

**File:** `web3/utils/exception_handling.py` (lines 42-58)

Contract-controlled URLs are requested via `requests` with no destination validation:

```python
session = requests.Session()
for url in offchain_lookup_payload["urls"]:
```

_Trimmed to 38 lines — full report: https://github.com/advisories/GHSA-5hr4-253g-cpx2_
