### Title
`deadline` field is overwritten by caller's raw non-canonical string after nonce is derived from the canonical `Date`, breaking `deadline === new Date(deadline).toISOString()` - ([File: packages/intents-sdk/src/intents/intent-payload-factory.ts])

### Summary
`defaultIntentPayloadFactory` computes a canonicalized `Date` from `params.deadline` and uses it to build `nonceDeadline`/`nonce`, but then spreads the original, un-canonicalized `params` object (which still contains the raw caller-supplied `deadline` string) over the return object, silently replacing the canonical `deadline: deadline.toISOString()` value with the caller's raw string. Any caller-provided `deadline` string that is not already byte-identical to its own `toISOString()` canonical form (extra fractional-second digits, non-`Z` timezone offset, etc.) ends up as the final signed `deadline` field, while the nonce embeds the canonical time.

### Finding Description
The equality that should hold is:
`signedPayload.deadline === new Date(signedPayload.deadline).toISOString()` and the instant encoded in `payload.deadline` should equal `nonceDeadline - DEFAULT_NONCE_DEADLINE_OFFSET_MS` (the same base instant used to derive the nonce).

In `defaultIntentPayloadFactory`: [1](#0-0) 

The destructuring `{ intents, verifying_contract, ...params }` does **not** remove `deadline` from `params` — only `intents` and `verifying_contract` are pulled out — so `params.deadline` still holds the attacker's exact original string. The function correctly parses this into a canonical `Date` and uses it to compute `nonceDeadline` and encode the nonce (`VersionedNonceBuilder.encodeNonce(salt, nonceDeadline)`), but the returned object list has `deadline: deadline.toISOString()` followed later by `...params`, and object spread applies later keys last — so `params.deadline` (the raw, non-canonical string) overwrites the canonical `deadline.toISOString()` value in the final returned payload.

An unprivileged caller of any SDK method that funnels a user-supplied `deadline` into `defaultIntentPayloadFactory` (e.g. `2026-01-01T00:00:00.264000Z` with 6 fractional digits, or `2026-01-01T05:00:00+05:00` with a non-Z offset) causes:
- The nonce to embed the canonical parsed instant (correct).
- The final signed `deadline` field to be the caller's raw string, verbatim.

Existing tests only exercise a `deadline` value already in canonical `toISOString()` form (`"2026-01-01T00:00:00.000Z"`), so the raw-string-equals-canonical-string case is never distinguished from the divergent case, and nothing in the factory or its test suite asserts `payload.deadline === new Date(payload.deadline).toISOString()`.

### Impact Explanation
Any downstream consumer, integrator, or auditor that only reads the signed intent's `deadline` field (rather than decoding the nonce) will compute an expiry that does not match the actual expiry embedded in the nonce that governs on-chain replay/expiry semantics comments in the file itself state "it's important they have the same value". This can cause a payload to be treated as still valid when the nonce's real embedded deadline has passed, or vice versa, potentially causing wrongful acceptance/rejection of a signed intent, double-processing decisions, or refund/credit logic based on a stale or misleading deadline string. This matches the Critical impact category (intent state disagreeing with what was actually signed/authorized, since a party can be misled about validity).

### Likelihood Explanation
No special privileges are required — any caller of an SDK path that accepts a user/integrator-controlled `deadline` and passes it to `defaultIntentPayloadFactory` can trigger this by supplying a `deadline` string with extra fractional-second precision or a non-`Z` timezone offset. This is a single-call, fully repeatable divergence with no dependency on route/token state, RPC behavior, or race conditions — it's a deterministic bug in object spread ordering.

### Recommendation
Remove `deadline` from `params` before spreading, or move the `...params` spread before setting `deadline`/`nonce` explicitly so the canonicalized value always wins, e.g.:
```ts
const { intents, verifying_contract, deadline: _rawDeadline, ...params } = input;
...
return {
  ...params,
  verifying_contract,
  deadline: deadline.toISOString(),
  nonce: VersionedNonceBuilder.encodeNonce(salt, nonceDeadline),
  intents: intents == null ? [] : intents,
  signer_id: undefined,
};
```

### Proof of Concept
```ts
import { describe, expect, it } from "vitest";
import { defaultIntentPayloadFactory } from "./intent-payload-factory";
import { VersionedNonceBuilder, type SaltedNonceValue } from "./expirable-nonce";

it("final deadline field diverges from canonical Date used for the nonce", () => {
  const salt = Uint8Array.from([1, 2, 3, 4]);
  // non-canonical: timezone offset instead of Z
  const rawDeadline = "2026-01-01T05:00:00+05:00";
  const canonical = new Date(rawDeadline).toISOString(); // "2026-01-01T00:00:00.000Z"

  const payload = defaultIntentPayloadFactory(salt, {
    verifying_contract: "intents.near",
    deadline: rawDeadline,
  });

  // BUG: payload.deadline is the raw string, not canonical
  expect(payload.deadline).toBe(rawDeadline);
  expect(payload.deadline === new Date(payload.deadline).toISOString()).toBe(false);

  // nonce was correctly derived from the canonical instant
  const decoded = VersionedNonceBuilder.decodeNonce(payload.nonce);
  const nonceDeadlineMs = Number(
    (decoded.value as SaltedNonceValue).inner.deadline / 1_000_000n,
  );
  expect(nonceDeadlineMs).toBe(new Date(canonical).getTime() + 60_000);
  // yet payload.deadline does not match `canonical`
  expect(payload.deadline).not.toBe(canonical);
});
```

### Citations

**File:** packages/intents-sdk/src/intents/intent-payload-factory.ts (L10-38)
```typescript
export function defaultIntentPayloadFactory(
	salt: Salt,
	{
		intents,
		verifying_contract,
		...params
	}: Partial<IntentPayload> & Pick<IntentPayload, "verifying_contract">,
): IntentPayload {
	// remove `undefined` properties
	params = Object.fromEntries(
		Object.entries(params).filter(([, value]) => value !== undefined),
	);

	const deadline =
		params.deadline != null
			? new Date(params.deadline)
			: new Date(Date.now() + DEFAULT_DEADLINE_MS);
	const nonceDeadline = new Date(
		deadline.getTime() + DEFAULT_NONCE_DEADLINE_OFFSET_MS,
	);

	return {
		verifying_contract,
		deadline: deadline.toISOString(),
		nonce: VersionedNonceBuilder.encodeNonce(salt, nonceDeadline),
		intents: intents == null ? [] : intents,
		signer_id: undefined, // or you can specify intent user id
		...params,
	};
```
