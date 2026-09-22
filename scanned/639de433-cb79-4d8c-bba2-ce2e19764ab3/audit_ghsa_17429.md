# [H] Finality Provider vulnerable to anti-slashing bypassing due to misconfiguration

## Summary
Severity: High
Advisory: GHSA-4jmp-x7mh-rgmr
CWE: CWE-285
Ecosystem: Go
CVSS: CVSS:4.0/AV:N/AC:L/AT:N/PR:N/UI:N/VC:N/VI:H/VA:N/SC:N/SI:N/SA:N (CVSS_V4)
Published: 2025-12-12
Source: https://github.com/advisories/GHSA-4jmp-x7mh-rgmr
Type: github-advisory

## Affected
- Go: `github.com/babylonlabs-io/finality-provider` — affected >=0 <1.0.4
- Go: `github.com/babylonlabs-io/finality-provider` — affected 1.1.0-rc.0
- Go: `github.com/babylonlabs-io/finality-provider` — affected 1.1.0-rc.1
- Go: `github.com/babylonlabs-io/finality-provider` — affected 1.99.0-devnet.6

## Details
### Summary

The anti-slashing is not effective if the attacker can access EOTS manager endpoints.

### Impact

If the EOTS manager endpoints are open to public without HMAC protection, the attacker can manually cause slashing of the finality provider through the RPC endpoints.

Report credits go to: x.com/RebelsRunways

## References
- https://github.com/babylonlabs-io/finality-provider/security/advisories/GHSA-4jmp-x7mh-rgmr
- https://github.com/babylonlabs-io/finality-provider/commit/721bf5b7a271ada1679a67496c9bc3516c339390
- https://github.com/babylonlabs-io/finality-provider
