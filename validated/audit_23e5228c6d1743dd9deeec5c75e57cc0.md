### Title
Caller-supplied non-ISO `deadline` overrides the normalized `deadline.toISOString()` in the signed payload, decoupling the textual expiry from the timestamp used to derive `nonceDeadline` - ([File: packages/intents-sdk/src/intents/intent-payload-factory.ts])

### Summary
In `defaultIntentPayloadFactory`, the object literal sets `deadline: deadline.toISOString()` but then spreads `...params` afterward, and `params` still retains the original, un-normalized `deadline` value the caller passed in. That raw string silently overwrites the computed ISO string in the returned, signed `IntentPayload`, while `nonceDeadline` (embedded in the nonce) is computed only from the parsed `Date` object.

### Finding Description
The claimed equality is: `payload.deadline === deadline.toISOString()` (which is what `nonceDeadline = new Date(deadline.getTime() + OFFSET)` is derived from).

Code path (`packages/intents-sdk/src/intents/intent-payload-factory.ts:10-38`):
```
const deadline = params.deadline != null ? new Date(params.deadline) : new Date(Date.now()+DEFAULT_DEADLINE_MS);
const nonceDeadline = new Date(deadline.getTime() + DEFAULT_NONCE_DEADLINE_OFFSET_MS);
return {
  ...
  deadline: deadline.toISOString(),
  nonce: VersionedNonceBuilder.encodeNonce(salt, nonceDeadline),
  ...
  ...params,   // <-- params.deadline (raw, un-normalized) is still present and overwrites the line above
};
```
`params` is derived via `{ intents, verifying_contract, ...params }` destructuring (line 12-16) and is only filtered for `undefined` values (line 19-21) — the original `deadline` string is never stripped from `params`. Because `...params` is spread last, whenever a caller supplies any `deadline` value, the final object's `deadline` field is literally the caller's raw string, not `deadline.toISOString()`.

This is reachable from `IntentExecuter.signAndSendIntent` (`packages/intents-sdk/src/intents/intent-executer-impl/intent-executer.ts:58-75`), which forwards arbitrary caller-supplied params (including `deadline`) straight into `defaultIntentPayloadFactory`. An ordinary SDK caller (an "unprivileged" integrator/user invoking the public `signAndSendIntent`/withdrawal APIs) can pass any string as `deadline`.

For a strictly ISO-8601 string (e.g., `"2025-07-30T12:57:16.264Z"`, as used in the existing test at `intent-executer.test.ts:149,159`), `deadline.toISOString()` reproduces the exact same string, so no divergence is observable. The bug only becomes observable with non-canonical-but-parseable inputs, e.g. `"2025-1-1"` or `"2025-06-01"` (date-only, no time/zone): `new Date(...)` still parses these to a concrete timestamp, `nonceDeadline` is computed from that timestamp, but the **signed** `deadline` field embeds the raw literal string instead of the canonical `toISOString()` form.

Important caveat for scoping actual impact: for date-only inputs like `"2025-06-01"`, the parsed timestamp equals `"2025-06-01T00:00:00.000Z"`, i.e., the same instant as `toISOString()` would produce — only the textual representation differs, not the underlying instant used for the nonce or for any downstream `new Date(payload.deadline)` re-parse. For genuinely ambiguous/non-standard inputs like `"2025-1-1"`, `Date` parsing is implementation-defined (not part of the ECMAScript-specified ISO subset), so different JS engines/runtimes (or the intents.near contract's own deadline parser, if it does not use the exact same lenient algorithm as V8) could interpret the same string as different instants — this is where a real divergence between "the instant the SDK used to compute nonceDeadline" and "the instant a downstream consumer computes by re-parsing `payload.deadline`" could theoretically occur.

I could not verify from the available index how the `intents.near` contract itself parses/validates the `deadline` field (its Rust deserializer's expected date format), nor whether it independently cross-checks the payload `deadline` against the nonce's embedded deadline. Without confirming the contract-side deadline parsing/validation behavior, I cannot conclusively demonstrate that this textual divergence causes the contract to enforce a *different* expiry than what bounds the nonce (as opposed to merely producing a payload with a non-canonical but still-consistent `deadline` string).

### Impact Explanation
If the contract (or any downstream indexer/relayer) independently parses `payload.deadline` and gets a different instant than what was used to compute `nonceDeadline`, the enforced expiry protecting the signed intent could diverge from the expiry embedded in the nonce, potentially allowing a signed intent to be considered valid/replayable outside its intended window. This would map to the "signature bound to the wrong... nonce" High-impact category from the spec — however, this depends entirely on contract-side parsing behavior, which is out of scope for this repo per the rules ("defects inside intents.near ... with no path through this repo") and which I was unable to confirm exists as an actual divergence rather than a purely SDK-internal cosmetic non-canonicalization.

### Likelihood Explanation
The caller must explicitly pass a non-canonical `deadline` string, which is only possible if an integrator's public-facing method forwards a raw, user-controlled deadline value into `signAndSendIntent`/`defaultIntentPayloadFactory` without normalizing it first — I could not confirm from the indexed code whether any public SDK-level API (e.g., withdrawal/swap methods on `sdk.ts`) actually exposes a raw `deadline` passthrough to unprivileged callers, versus `deadline` being an internal-only knob used by SDK-authored `intentPayloadFactory` hooks (as seen in the tests, which are developer-supplied factories, not attacker input).

### Recommendation
Strip `deadline` from `params` after parsing it (mirroring how `intents` and `verifying_contract` are already destructured out), so the canonical `deadline.toISOString()` cannot be overwritten by the raw input:
```ts
const { intents, verifying_contract, deadline: _rawDeadline, ...params } = ...;
```
And ensure `payload.deadline` is always exactly `deadline.toISOString()`.

### Proof of Concept
Could not be finalized with high confidence because it depends on unverified contract-side deadline parsing behavior. A minimal vitest reproduction of the SDK-level equality break (independent of contract behavior) would be:
```ts
const payload = defaultIntentPayloadFactory(salt, {
  verifying_contract: "intents.near",
  deadline: "2025-06-01",
});
const canonical = new Date("2025-06-01").toISOString(); // "2025-06-01T00:00:00.000Z"
expect(payload.deadline).not.toBe(canonical); // fails today: payload.deadline === "2025-06-01"
```
This confirms the SDK-internal equality break (`payload.deadline !== deadline.toISOString()`), but I cannot confirm without contract-level context whether this leads to an actual expiry-enforcement divergence that satisfies the High-impact bar, so I am not asserting a confirmed exploitable vulnerability. [1](#0-0) [2](#0-1) [3](#0-2)

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

**File:** packages/intents-sdk/src/intents/intent-executer-impl/intent-executer.ts (L58-75)
```typescript
	async signAndSendIntent({
		relayParams: relayParamsFactory,
		salt,
		signedIntents,
		...intentParams
	}: {
		relayParams?: IntentRelayParamsFactory;
		salt: Salt;
		signedIntents?: SignedIntentsComposition;
	} & Partial<Parameters<IntentPayloadFactory>[0]>): Promise<{
		ticket: Ticket;
	}> {
		const verifyingContract = this.envConfig.contractID;

		let intentPayload = defaultIntentPayloadFactory(salt, {
			verifying_contract: verifyingContract,
			...intentParams,
		});
```

**File:** packages/intents-sdk/src/intents/shared-types.ts (L5-15)
```typescript
export interface IntentPayload {
	verifying_contract: string;
	deadline: string;
	nonce: string;
	intents: IntentPrimitive[];
	signer_id: string | undefined;
}

export type IntentPayloadFactory = (
	intentParams: IntentPayload,
) => Promise<Partial<IntentPayload>> | Partial<IntentPayload>;
```
