### No vulnerability found for this question.

**Reasoning:**

The premise that "the error type does not distinguish 'unknown' from 'failed'" is factually incorrect for this code path. `watchWithdrawal` in `packages/intents-sdk/src/core/withdrawal-watcher.ts` uses two distinct, differently-named error classes:

- `WithdrawalFailedError` — thrown only when the bridge itself explicitly reports `status.status === "failed"` [1](#0-0) , i.e. a genuine terminal failure signal from the bridge/adapter.
- `WithdrawalWatchError` — thrown only on `PollTimeoutError` (the derived p99*3(+HOT extra) timeout) or after `MAX_CONSECUTIVE_ERRORS` transient RPC/API failures [2](#0-1) . This class name and its constructor message (`"Withdrawal watch failed"`, distinct `cause`) explicitly signal "the SDK stopped watching / unknown outcome," not "the withdrawal failed on-chain/on-bridge."

These are separate exported types (`WithdrawalFailedErrorType` vs `WithdrawalWatchErrorType`) with different `name` fields [3](#0-2) , so any integrator inspecting `err.name` (or using `instanceof`) can and must distinguish "definitely failed" from "unknown/timed out, may still complete." The SDK never collapses these into one throw path, and `watchWithdrawal` never returns/throws a "failed" signal for a case where the bridge might still deliver — it only ever does that when the bridge itself reports `failed`.

The exploit as framed requires an integrator to deliberately (or mistakenly) treat `WithdrawalWatchError` — which is explicitly and by design an "unknown" outcome — as equivalent to `WithdrawalFailedError` and issue a refund on that basis. That is an integration-level misuse of a documented, distinguishable error type, not a defect in the traced SDK code path (`getWithdrawalStatsForChain` / `watchWithdrawal`). Per the rules, this falls under "requiring the integrator to deliberately misuse a documented escape hatch," and no code in the target path actually produces a mislabeled terminal-failure signal for a withdrawal that can still complete.

Additionally, the attacker-controlled inputs listed (destination chain choice, HOT batch size affecting sequential wait time, submission timing) only affect *when* a timeout/`WithdrawalWatchError` occurs, not *whether* the SDK reports it as `WithdrawalFailedError`. There is no reachable path where the equality "bridge delivers funds" vs. "SDK reports terminal failed" actually breaks in the SDK's own type system — the ambiguity, if any, is purely at the integrator's response-handling layer, which is outside this repo's control and outside the defined attack surface (no `intents`, `amount`, `receiver_id`, `nonce`, `feeEstimation`, or `WithdrawalIdentifier.index` value is altered or misreported by this code).

### Citations

**File:** packages/intents-sdk/src/core/withdrawal-watcher.ts (L49-51)
```typescript
					if (status.status === "failed") {
						throw new WithdrawalFailedError(status.reason);
					}
```

**File:** packages/intents-sdk/src/core/withdrawal-watcher.ts (L59-77)
```typescript
					consecutiveErrors++;
					if (consecutiveErrors >= MAX_CONSECUTIVE_ERRORS) {
						throw new WithdrawalWatchError(err);
					}

					args.logger?.warn(
						`Transient error (${consecutiveErrors}/${MAX_CONSECUTIVE_ERRORS}): ${err}`,
					);
					return POLL_PENDING;
				}
			},
			{ stats, signal: args.signal },
		);
	} catch (err: unknown) {
		if (err instanceof PollTimeoutError) {
			throw new WithdrawalWatchError(err);
		}
		throw err;
	}
```

**File:** packages/intents-sdk/src/core/withdrawal-watcher.ts (L129-152)
```typescript
export type WithdrawalFailedErrorType = WithdrawalFailedError & {
	name: "WithdrawalFailedError";
};

export class WithdrawalFailedError extends BaseError {
	constructor(reason: string) {
		super(`Withdrawal failed: ${reason}`, {
			name: "WithdrawalFailedError",
		});
	}
}

export type WithdrawalWatchErrorType = WithdrawalWatchError & {
	name: "WithdrawalWatchError";
};

export class WithdrawalWatchError extends BaseError {
	constructor(cause: unknown) {
		super("Withdrawal watch failed", {
			name: "WithdrawalWatchError",
			cause,
		});
	}
}
```
