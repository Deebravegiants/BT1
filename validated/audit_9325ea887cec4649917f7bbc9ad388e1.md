Found it: `pallet-bandwidth`'s `PurchaseMessage::try_from` (`modules/pallets/bandwidth/src/abi.rs:35-67`) feeds a fully attacker-controlled `chain: bytes` field straight into `StateMachine::from_str` (`modules/ismp/core/src/host.rs:344-426`), and that parser resolves ambiguous, delimiter-split identifiers by silently taking `split('-').last()` — a direct structural analog of samlify's "text-context data is not escaped/bounded" flaw.

### Title
Delimiter-Confusion in `StateMachine::from_str` Lets an Unprivileged Bandwidth Purchaser Redirect Credit to an Unintended Chain - (modules/ismp/core/src/host.rs)

### Summary
`evm/src/apps/BandwidthManager.sol::purchase()` accepts a caller-supplied `bytes chain` field with no format validation beyond non-empty (`chain.length == 0` check at [1](#0-0) ), packs it verbatim into `BandwidthPurchaseMsg.chain` ( [2](#0-1) ), and dispatches it to `pallet-bandwidth`. On the receiving side, `PurchaseMessage::try_from` decodes this untrusted UTF-8 string and parses it with `StateMachine::from_str` ( [3](#0-2) ). That parser only checks a string *prefix* (`starts_with("EVM-")`, `starts_with("RELAY-")`, etc.) and then extracts the identifier by naive `'-'`-delimiter splitting, taking `.last()` for numeric ids or `.get(1)` for the RELAY 4-byte consensus id ( [4](#0-3) ). Because the prefix check does not require the remainder to be a *single* token, an attacker can embed extra `-`-delimited segments inside the value without the resulting parse failing.

### Finding Description
This is structurally identical to the samlify bug: a boundary character (`"`  in XML attribute context vs. `-` here) is trusted to delimit a field, but the consuming code only validates a prefix/shape and then greedily re-splits on that same delimiter, silently discarding or merging attacker-supplied segments instead of rejecting malformed input.

Concretely:
- `"EVM--<n>"`, `"EVM-1-2-3"`, or any `"EVM-...-<attacker_id>"` string starts with `"EVM-"` and passes the `starts_with` gate, then `split('-').last()` extracts whatever trailing numeric token the attacker wants, discarding everything else in the string [5](#0-4) .
- For `"RELAY-"`, `values.get(1)` (the second `'-'`-delimited token) is taken as the 4-byte relay id and `values.last()` as `para_id`, with everything between silently dropped — two independent-looking substrings of the same string can be stitched together into a *different* `StateMachine::Relay{relay, para_id}` value than what a human or auditor reading the whole string would expect [6](#0-5) .

The pallet performs **no additional validation** that the parsed `StateMachine` corresponds to the literal string supplied — it directly uses the parsed enum as the storage key for crediting bandwidth: `Self::push_subscription(&msg.chain, &key, tier, bytes, duration)` and emits `BandwidthCredited { app_chain: msg.chain, ... }` ( [7](#0-6) ). The `chain` argument is explicitly documented as *not* validated against the request source (sponsorship is a deliberate feature) ( [8](#0-7) ), so the pallet's only real defense against a caller lying about which chain to credit is that the string must *literally* denote that chain. The `.last()`/`.get(1)` parsing breaks that guarantee: a string can be crafted to look benign in logs/events while resolving to an entirely different `StateMachine` than its apparent content, or two semantically different attacker-chosen byte strings can resolve to the exact same enum value that governance did not intend to alias.

### Impact Explanation
This does not directly mint funds, but it corrupts the trust boundary the sponsorship feature depends on: bandwidth accounting (`Allowance<T>` keyed by `(app_chain, app)`) can be credited to a `StateMachine` value that does not match what auditors, monitoring, or off-chain event consumers infer from the raw `chain` bytes in `BandwidthPurchased`/`BandwidthCredited` events, because the emitted event carries the raw attacker bytes ( [9](#0-8)  and [10](#0-9) ) while the actual storage key is the ambiguously-parsed enum. This is a state-commitment/routing-integrity defect (CWE-707/CWE-20 class, same root cause as the SAML CWE-91 report: unescaped delimiter reuse causing structural reinterpretation) reachable by any unprivileged caller of `purchase()`, and the same `StateMachine::from_str` is also used to reconstruct `PostRequest.source`/`dest` from EVM `PostRequestEvent` strings on the relayer/tesseract side ( [11](#0-10) ), so the ambiguity is not confined to one call site.

### Likelihood Explanation
High reachability (any address can call `BandwidthManager.purchase()` with an arbitrary `chain` byte string, paying only the tier price), but the *severity* of the outcome depends on whether a downstream consumer relies on the literal string matching the parsed enum for security decisions elsewhere; within the code reviewed, no such secondary check exists in `pallet-bandwidth`, so the practical damage is limited to bookkeeping/audit-trail confusion rather than a full fund-theft primitive.

### Recommendation
In `StateMachine::from_str`, require that after stripping the recognized prefix, the remainder contains **exactly** the expected number of `'-'`-delimited segments (reject if `split('-').count()` doesn't match the variant's expected arity) instead of using `.last()`/`.get(1)`, mirroring how XML/SAML fixes require escaping or strict tokenization rather than best-effort boundary recovery.

### Proof of Concept
Not independently executed; based on static analysis of `modules/ismp/core/src/host.rs:344-426`, `modules/pallets/bandwidth/src/abi.rs:35-67`, and `evm/src/apps/BandwidthManager.sol:153-200`. A call such as `purchase(app, tier, months, bytes("EVM-1-999999"))` would pass `chain.length != 0`, be ABI-encoded and dispatched, and on the pallet side `StateMachine::from_str("EVM-1-999999")` would return `StateMachine::Evm(999999)` (last split segment) despite the string appearing to reference chain `EVM-1`.

### Citations

**File:** evm/src/apps/BandwidthManager.sol (L157-159)
```text
        if (app.length == 0 || app.length > MAX_APP_LENGTH || chain.length == 0 || months == 0) {
            revert InvalidPurchase();
        }
```

**File:** evm/src/apps/BandwidthManager.sol (L172-177)
```text
        BandwidthPurchaseMsg memory body = BandwidthPurchaseMsg({
            app: app,
            tier: tier,
            months: months,
            chain: chain
        });
```

**File:** evm/src/apps/BandwidthManager.sol (L190-199)
```text
        emit BandwidthPurchased({
            payer: msg.sender,
            feeToken: feeToken,
            tier: tier,
            months: months,
            amountPaid: amount,
            app: app,
            chain: chain,
            commitment: commitment
        });
```

**File:** modules/pallets/bandwidth/src/abi.rs (L60-63)
```rust
		let chain_str = str::from_utf8(&abi.chain)
			.map_err(|err| anyhow::anyhow!(format!("chain is not utf-8: {err}")))?;
		let chain = StateMachine::from_str(chain_str)
			.map_err(|err| anyhow::anyhow!(format!("invalid chain {chain_str:?}: {err}")))?;
```

**File:** modules/ismp/core/src/host.rs (L344-386)
```rust
impl FromStr for StateMachine {
	type Err = String;

	fn from_str(s: &str) -> Result<Self, Self::Err> {
		let s = match s {
			name if name.starts_with("EVM-") => {
				let id = name
					.split('-')
					.last()
					.and_then(|id| u32::from_str(id).ok())
					.ok_or_else(|| format!("invalid state machine: {name}"))?;
				StateMachine::Evm(id)
			},
			name if name.starts_with("POLKADOT-") => {
				let id = name
					.split('-')
					.last()
					.and_then(|id| u32::from_str(id).ok())
					.ok_or_else(|| format!("invalid state machine: {name}"))?;
				StateMachine::Polkadot(id)
			},

			name if name.starts_with("RELAY-") => {
				let values = name.split('-').collect::<Vec<_>>();
				let id = values
					.last()
					.and_then(|id| u32::from_str(id).ok())
					.ok_or_else(|| format!("invalid state machine: {name}"))?;
				let relay = values
					.get(1)
					.and_then(|id| {
						let bytes = id.as_bytes();
						if bytes.len() == 4 {
							let mut dest = [0u8; 4];
							dest.copy_from_slice(bytes);
							Some(dest)
						} else {
							None
						}
					})
					.ok_or_else(|| format!("invalid state machine: {name}"))?;
				StateMachine::Relay { relay, para_id: id }
			},
```

**File:** modules/pallets/bandwidth/src/lib.rs (L473-486)
```rust
			let bytes = cfg.bytes.saturating_mul(msg.months as u128);
			let duration = cfg.duration_secs.saturating_mul(msg.months as u64);

			let key = AppKey::truncate_from(msg.app);
			let expires_at = Self::push_subscription(&msg.chain, &key, tier, bytes, duration);

			Self::deposit_event(Event::BandwidthCredited {
				app_chain: msg.chain,
				app: key,
				paid_from: request.source,
				tier,
				bytes,
				expires_at,
			});
```

**File:** docs/content/developers/evm/bandwidth/purchasing.mdx (L192-205)
```text
## Sponsoring Another Chain

The `chain` argument is **not validated against the source chain** — see [Overview → Sponsorship](/developers/evm/bandwidth/overview#sponsorship) for the model. A buyer on Ethereum credits an app on Base by passing the credit chain id in `chain`:

```solidity
manager.purchase({
    app:    abi.encodePacked(appAddressOnBase),
    tier:   2,
    months: 6,
    chain:  bytes("EVM-8453")
});
```

The pallet keys allowance storage on `(msg.chain, msg.app)`, so the credit lands on Base regardless of which chain sent the payment. The recommended pattern for teams running a central treasury is to deploy `BandwidthManager` on one low-fee chain and sponsor bandwidth for app instances elsewhere.
```

**File:** modules/ismp/core/src/abi.rs (L294-308)
```rust
impl TryFrom<PostRequestEvent> for router::PostRequest {
	type Error = anyhow::Error;

	fn try_from(post: PostRequestEvent) -> Result<Self, Self::Error> {
		Ok(router::PostRequest {
			source: StateMachine::from_str(&post.source).map_err(|e| anyhow!("{}", e))?,
			dest: StateMachine::from_str(&post.dest).map_err(|e| anyhow!("{}", e))?,
			nonce: post.nonce.try_into().map_err(|e| anyhow!("{e}"))?,
			from: post.from.0.to_vec(),
			to: post.to.0.to_vec(),
			timeout_timestamp: post.timeoutTimestamp.try_into().map_err(|e| anyhow!("{e}"))?,
			body: post.body.to_vec(),
		})
	}
}
```
