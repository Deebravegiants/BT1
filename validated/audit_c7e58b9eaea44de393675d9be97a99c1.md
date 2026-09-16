I found a strong analog: `TransactionInfo::succeeded` in the TRON messaging relayer, which classifies transaction outcomes using the exact "one bad-status value blacklisted, everything else treated as good" pattern that caused CVE-2024-8096. [1](#0-0) 

### Title
Incomplete TRON transaction-outcome check treats non-"FAILED" execution results as success - (File: tesseract/messaging/tron/src/api.rs)

### Summary
`TransactionInfo::succeeded` falls back to `self.result.as_deref() != Some("FAILED")` when no `receipt` is present, mirroring the curl OCSP bug class where only one specific bad value ("revoked"/here, "FAILED") is checked and every other outcome — including other explicit failure/error states TRON's API can return (e.g. `"REVERT"`, `"OUT_OF_ENERGY"`, `"CONTRACT_VALIDATE_ERROR"`, `"DEFAULT"`, unset/null result on a rejected broadcast) — is silently accepted as success.

### Finding Description
`TransactionInfo` models the TRON `gettransactioninfobyid` response and exposes `succeeded()` for the relayer to decide whether a submitted TRON transaction actually landed: [1](#0-0) 
When a full `receipt` is present, the check correctly requires `receipt.result == Some("SUCCESS")` (an allow-list, correctly conservative). But the `else` branch — taken whenever `receipt` is `None` — inverts the logic to a deny-list: it only rejects when `result == "FAILED"`, and calls everything else including `None` (result field absent because the node hasn't finished processing, or the transaction never executed), `"REVERT"`, `"OUT_OF_ENERGY"`, `"OUT_OF_TIME"`, `"OUT_OF_MEMORY"`/other VM abort codes a success. This is structurally identical to the curl OCSP bug: instead of checking "is this the one accepted-good value", it checks "is this the one specific known-bad value", so any bad status the author didn't enumerate is misclassified as good.

This function feeds `wait_for_success`-equivalent confirmation logic in the TRON relayer path (`tesseract/messaging/tron`), which an unprivileged relayer process uses to decide whether a dispatched cross-chain message/settlement transaction actually executed on TRON before it reports delivery/finality upstream to the rest of the bridge pipeline.

### Impact Explanation
If a TRON transaction that dispatches an ISMP message, delivers a proof, or executes a token-bridge mint/burn reverts on-chain (returning a `result` other than the literal string `"FAILED"`, e.g. `"REVERT"`/`"OUT_OF_ENERGY"` in the no-receipt branch, or before the receipt is populated), the relayer's `succeeded()` check reports success. This can cause the relayer to treat an on-chain revert as a successful delivery — forging confirmation of a message that was never actually executed on the destination, or reporting a fee/settlement transaction as delivered when funds never moved, leading to accounting/state desync (unbacked confirmation of delivery, incorrect relayer fee claims, or forged completion status) between the TRON leg and the rest of Hyperbridge.

### Likelihood Explanation
Reachable purely from relaying normal TRON transactions; it is not a rare edge case since the no-`receipt` branch is documented as occurring "in many TRON node versions" on success — meaning it is regularly exercised, and any transient revert/energy-exhaustion during that same window is misreported. No malicious admin/governance/collator action is required — an ordinary relayer node processing a normal request triggers this path.

### Recommendation
Invert the no-receipt branch to an allow-list matching the receipt-present branch: treat the transaction as successful only when `result` is explicitly `Some("SUCCESS")` (or `None` combined with an independent, verified confirmation such as re-querying `getTransactionInfoById` until a definitive result/receipt is available), and treat every other value — `None`, `"FAILED"`, `"REVERT"`, `"OUT_OF_ENERGY"`, etc. — as not-yet-confirmed/failed rather than success.

### Proof of Concept
1. Relayer submits a TRON transaction (e.g. delivering a Hyperbridge message) via `broadcast`/`into_result`.
2. Node executes the transaction and it reverts with `result: "REVERT"` (or any status besides "FAILED"), with `receipt` still `None` in the immediate query window (a documented normal occurrence per the code comment).
3. Relayer calls `TransactionInfo::succeeded()`, which evaluates `self.result.as_deref() != Some("FAILED")` → `"REVERT" != "FAILED"` → `true`.
4. The relayer treats the reverted transaction as successfully delivered/confirmed and proceeds, propagating an unbacked delivery confirmation through the bridge pipeline.

### Citations

**File:** tesseract/messaging/tron/src/api.rs (L484-495)
```rust
impl TransactionInfo {
	/// `true` if the contract execution succeeded.
	pub fn succeeded(&self) -> bool {
		// `result` is absent on success in many TRON node versions,
		// but `receipt.result` should be "SUCCESS".
		if let Some(ref receipt) = self.receipt {
			receipt.result.as_deref() == Some("SUCCESS")
		} else {
			// If there's no receipt, check the top-level result field
			self.result.as_deref() != Some("FAILED")
		}
	}
```
