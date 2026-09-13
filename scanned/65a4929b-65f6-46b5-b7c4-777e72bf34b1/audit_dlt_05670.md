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

AI assistance used for investigation, patching, and validation.

Co-authored-by: lodekeeper <lodekeeper@users.noreply.github.com>

### packages/beacon-node/src/api/impl/beacon/blocks/index.ts
```diff
@@ -776,9 +776,9 @@ export function getBeaconBlockApi({
       // Track metrics for data column publishing
       if (dataColumnSidecars.length > 0) {
         let columnsPublishedWithZeroPeers = 0;
-        // Skip first entry (envelope), track data columns
-        for (let i = 1; i < sentPeersArr.length; i++) {
-          const sentPeers = sentPeersArr[i] as number;
+        // Skip first entry (envelope); the final entry is processExecutionPayload(), which returns void.
+        for (let i = 0; i < dataColumnSidecars.length; i++) {
+          const sentPeers = sentPeersArr[i + 1] as number;
           metrics?.dataColumns.sentPeersPerSubnet.observe(sentPeers);
           if (sentPeers === 0) {
             columnsPublishedWithZeroPeers++;
```
