### Title
`parsePublishIntentsResponse` trusts relay's `intent_hashes` on "already processed" without validating length/order against submitted `multiPayloads` - ([File: packages/internal-utils/src/solverRelay/publishIntents.ts])

### Summary
`parsePublishIntentsResponse` returns `Ok(response.intent_hashes)` for any `FAILED` response whose `reason === "already processed"`, without checking that `intent_hashes.length` equals `publishParams.signed_datas.length` or that the hashes are in the same order as the submitted multiPayloads. This result flows unchanged through `IntentRelayerPublic.publishIntents` into `sdk.sendSignedIntents`, so `tickets[i]` can silently stop corresponding to `multiPayloads[i]`.

### Finding Description
The equality the SDK relies on is: for a batch call `sendSignedIntents({multiPayloads})`, the returned `tickets` array must satisfy `tickets[i] identifies the settlement of multiPayloads[i]` for every `i`.

Trace:
- `sdk.sendSignedIntents` (packages/intents-sdk/src/sdk.ts:622-636) calls `this.intentRelayer.publishIntents({multiPayloads, quoteHashes}, ...)` and returns `{ tickets }` verbatim — no re-indexing, no length check.
- `IntentRelayerPublic.publishIntents` (packages/intents-sdk/src/intents/intent-relayer-impl/intent-relayer-public.ts:45-71) calls `solverRelay.publishIntents({quote_hashes, signed_datas: multiPayloads}, ...)` and returns `result.unwrap() as IntentHash[]` directly.
- `solverRelay.publishIntents` → `parsePublishIntentsResponse` (packages/internal-utils/src/solverRelay/publishIntents.ts:53-66):
```
if (response.status === "OK") { return Ok(response.intent_hashes); }
if (response.reason === "already processed") { return Ok(response.intent_hashes); }
return Err(toRelayPublishError(publishParams, response));
```
- The underlying HTTP layer (`packages/internal-utils/src/solverRelay/solverRelayHttpClient/apis.ts:30-41`) casts the JSON-RPC result `as any` with no runtime schema validation of `intent_hashes` length or content against the number of `signed_datas` submitted (`types.ts:104-116` defines `PublishIntentsResponseFailure.intent_hashes: string[]` with no cardinality constraint tied to the request).

Root cause: the code assumes that whenever the relay reports "already processed", the `intent_hashes` field is a complete, correctly-ordered array matching the just-submitted `multiPayloads`. Nothing enforces this. If the relay (on a resubmission after a timeout, partial-batch dedup, or any batch where only some sub-intents were previously processed) returns a truncated, empty, or differently-ordered `intent_hashes` array, `parsePublishIntentsResponse` still returns `Ok` with that array as-is.

Existing guards inspected: there is no `validateAddress`/`compareAddresses`/`matchesRequest` style check anywhere between the relay response and `sdk.sendSignedIntents`'s return; no assertion compares `tickets.length` to `multiPayloads.length`. The single-intent path `publishIntent` (intent-relayer-public.ts:22-42) even blindly reads `(...)[0]!` assuming at least one element exists, reinforcing the pattern of trusting array shape without validation. Nothing in the intents contract mitigates this because the mismatch happens purely in SDK-side bookkeeping between ticket and payload before any settlement wait occurs.

### Impact Explanation
If the array is misaligned, the caller's `tickets[i]` is bound to the wrong `multiPayload`. An integrator calling `sdk.waitForIntentSettlement(tickets[i])` (or the analogous relayer `waitForSettlement`) will get on-chain settlement confirmation for a different signed intent than the one at `multiPayloads[i]`. This can cause the integrator to credit or refund a user based on the wrong intent's outcome — e.g., confirming settlement of a smaller/larger transfer, or reporting the wrong recipient's payload as settled — a misreport that leads to double-crediting or crediting for an unrelated intent. This matches the High/Critical category "a status or hash misreport making an integrator credit or refund twice."

### Likelihood Explanation
Preconditions: caller must invoke `sendSignedIntents`/`publishIntents` with more than one `MultiPayload` in a batch, and a resubmission (e.g., after a client-side timeout/retry) must hit a relay state where some but not all of the batch was already processed, or the relay's "already processed" response for that batch does not enumerate hashes 1:1 in submission order for the full batch. This depends on relay-side behavior; the vulnerable code path itself, however, is reachable by any caller (unprivileged) using standard SDK batch APis and requires no special access — it is a client-controlled scenario (network retry) rather than an attacker exploiting a third party, but it is squarely a code defect in this repo since no verification exists to catch or reject a malformed/mismatched response before returning it as trustworthy tickets.

### Recommendation
In `parsePublishIntentsResponse`, before returning `Ok(response.intent_hashes)` for the `"already processed"` branch (and ideally also for the `"OK"` branch), validate that `response.intent_hashes.length === publishParams.signed_datas.length`. If lengths mismatch, return an `Err` (e.g. a new `RelayPublishResultUnknownError`/dedicated mismatch error) rather than silently returning a partial/misaligned array. If possible, recompute expected intent hashes locally from `publishParams.signed_datas` (as done in `computeIntentHash`) and cross-check them against `response.intent_hashes` positionally instead of trusting the relay's ordering blindly.

### Proof of Concept
```ts
// packages/internal-utils/src/solverRelay/publishIntents.test.ts (new case)
import { http, HttpResponse } from "msw";
import { describe, expect, it } from "vitest";
import { server } from "../../test/setup";
import { publishIntents } from "./publishIntents";
import type { PublishIntentsResponse } from "./solverRelayHttpClient/types";

it("BUG: returns truncated intent_hashes as Ok on 'already processed' for a 2-payload batch", async () => {
  server.use(
    http.post("https://solver-relay-v2.chaindefuser.com/rpc", () => {
      return HttpResponse.json({
        id: "dontcare",
        jsonrpc: "2.0",
        result: {
          intent_hashes: ["onlyOneHash"], // expected 2, only 1 returned
          status: "FAILED",
          reason: "already processed",
        },
      } satisfies PublishIntentsResponse);
    }),
  );

  const signedDatas = [
    { payload: "p1", signature: "s1", standard: "erc191" as const },
    { payload: "p2", signature: "s2", standard: "erc191" as const },
  ];

  const result = await publishIntents({ quote_hashes: [], signed_datas: signedDatas });

  // Equality claimed by the SDK: tickets.length === multiPayloads.length
  // Actual: result is Ok(['onlyOneHash']) with length 1, not 2 -> mismatch proven
  expect(result.isOk()).toBe(true);
  expect(result.unwrap()).toEqual(["onlyOneHash"]);
  expect(result.unwrap().length).not.toBe(signedDatas.length); // demonstrates broken invariant
});
```
This confirms `sdk.sendSignedIntents({multiPayloads: [a, b]})` would resolve `tickets` of length 1 (or reordered), so `tickets[i]` downstream no longer identifies `multiPayloads[i]`.