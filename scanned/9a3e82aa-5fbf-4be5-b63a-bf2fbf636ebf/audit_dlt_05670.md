# [?] fix: avoid metrics crash on payload envelope publish (#9279)

## Summary
Severity: Unknown
Chain: Ethereum
Component: ChainSafe/lodestar
Published: 2026-04-25
Source: https://github.com/ChainSafe/lodestar/commit/7a6a5b0190e5e2e7ac39c234e3f5dbab958739af
Type: security-commit

## Details
fix: avoid metrics crash on payload envelope publish (#9279)

## Summary
- fix the `publishExecutionPayloadEnvelope()` metrics loop so it only
records sent-peer counts for actual data-column publishes
- avoid feeding the trailing `processExecutionPayload()` `void` result
into the Prometheus histogram
- prevent the false REST 500 Barnabas reported (`Value is not a valid
number: undefined`)

## Root cause
`publishExecutionPayloadEnvelope()` builds a `publishPromises` array
with:
1. envelope publish
2. each data column publish
3. `chain.processExecutionPayload(...)`

The handler then iterated through `sentPeersArr.length` when recording
`metrics.dataColumns.sentPeersPerSubnet`, which included the final
`void` result from `processExecutionPayload()`. That led to
`observe(undefined)` and a thrown `prom-client` type error.

## Fix
Mirror the older block-publish path and iterate only over
`dataColumnSidecars.length`, using the existing `+1` offset to skip the
envelope publish entry.

## Validation
- reproduced the root cause locally on `glamsterdam-devnet-0`
- verified the patched build no longer throws `Value is not a valid
number: undefined`
- forced the exact local API path via:
  - `GET /eth/v1/beacon/execution_payload_envelope/head`
  - replay to `POST /eth/v1/beacon/execution_payload_envelope`
- after the patch, the replay no longer crashes in metrics; it now
returns `EXECUTION_PAYLOAD_ENVELOPE_ERROR_ALREADY_KNOWN`, which is
consistent with duplicate-envelope handling rather than the original bug


_Trimmed to 38 lines — full report: https://github.com/ChainSafe/lodestar/commit/7a6a5b0190e5e2e7ac39c234e3f5dbab958739af_
