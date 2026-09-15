# [H] atomic-agents-stack: Parallel helper/delegate batch reserves $0 for models absent from the pricing table, bypassing the cost-cap fan-out guard

## Summary
Severity: High
Advisory: GHSA-j659-8xh6-5pq5
CWE: CWE-770
Ecosystem: PyPI
CVSS: CVSS:4.0/AV:N/AC:L/AT:N/PR:N/UI:N/VC:N/VI:H/VA:N/SC:N/SI:N/SA:N (CVSS_V4)
Published: 2026-08-17
Source: https://github.com/advisories/GHSA-j659-8xh6-5pq5
Type: github-advisory

## Affected
- PyPI: `atomic-agents-stack` — affected >=0 <1.1.0

## Details
`_estimate_batch_cost` (`atomic_agents/agent.py`) looks up the per-model output price with `PRICING.get(model, {})`, returning 0.0 for any model not in the hardcoded pricing table. `_check_batch_reservation` then early-returns when the reservation is <= 0, skipping the batch reservation entirely. That reservation is the only defense against the documented fan-out race where every parallel helper/delegate reads the identical pre-batch on-disk cost total and each passes its individual check even though the collective spend overruns the configured cap.

**Impact:** an operator running any model not in the pricing table (self-hosted/Ollama/vLLM, a new provider SKU) with `cost_guardrails` + `daily_cap_usd` set believes the cap protects them, but a single parallel batch can blow past the cap. The parallel-helper `model` argument can also be steered to an unknown id. The sibling `dream._estimate_dream_cost` does this correctly (`PRICING.get(model, _fallback_pricing())`), which makes this a clear defect.

**Affected:** `agent.py` (`_estimate_batch_cost` / `_check_batch_reservation`), all versions through 1.0.0.

**Fix:** use `PRICING.get(model, _costs._fallback_pricing())['output']` (mirror dream/calc_cost). Add a conformance test asserting an unknown-model batch reserves > 0 and that an over-cap unknown-model batch raises `CostGuardrailBlocked`.

## References
- https://github.com/dep0we/atomic-agents-stack/security/advisories/GHSA-j659-8xh6-5pq5
- https://github.com/dep0we/atomic-agents-stack
- https://github.com/dep0we/atomic-agents-stack/releases#release-v1.1.0
