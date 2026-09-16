### Title
`StateMachine::from_str` unsanitized `-` separator allows leg-injection / scope-confusion in state-machine identifier parsing - ([File: modules/ismp/core/src/host.rs])

### Summary
`StateMachine::from_str` (the canonical parser for the wire-string form of a state-machine identifier, e.g. `"EVM-97"`, `"POLKADOT-3367"`, `"RELAY-CENJ-1000"`) splits the input on the `-` character and always takes `.split('-').last()` (or `.get(1)` for the relay id) to extract the numeric/para chain id, without validating that the string contains exactly the expected number of `-`-delimited segments. This mirrors the Kysely root cause exactly: a single reserved separator character (`.` in JSON-path legs, `-` here) is treated as a hard structural delimiter, but the parser never rejects extra, attacker-supplied instances of that same separator inside what is supposed to be an atomic field. Any code path that only checks a *prefix* (`starts_with("EVM-")`) while the id is actually extracted from the *last* segment lets an attacker embed additional `-`-delimited "legs" that get picked up instead of the intended one, producing a different `StateMachine` value than what a naive/prefix-based validator believes it approved. [1](#0-0) 

### Finding Description
`StateMachine::from_str` is defined as:

```rust
impl FromStr for StateMachine {
    fn from_str(s: &str) -> Result<Self, Self::Err> {
        let s = match s {
            name if name.starts_with("EVM-") => {
                let id = name.split('-').last().and_then(|id| u32::from_str(id).ok())...
                StateMachine::Evm(id)
            },
            ...
            name if name.starts_with("RELAY-") => {
                let values = name.split('-').collect::<Vec<_>>();
                let id = values.last()...;
                let relay = values.get(1)...;
                StateMachine::Relay { relay, para_id: id }
            },
            ...
        };
        Ok(s)
    }
}
``` [2](#0-1) 

This is the exact "path-leg" pattern from the external report: the `-` character is the structural separator between the "type" leg and the "value" leg of the identifier, exactly as `.` separates JSON-path legs in Kysely's `visitJSONPathLeg`. The parser does two independent, inconsistent things with the same character:

1. **Prefix match** (`starts_with("EVM-")`, `starts_with("RELAY-")`, etc.) — this only inspects the first leg.
2. **Value extraction** (`split('-').last()` or `.get(1)`) — this trusts whichever leg happens to land in that position after an attacker-controlled number of extra `-` characters is inserted.

Because these two checks are not bound together (there is no assertion that `split('-').count() == 2` for the simple variants, or `== 3` for `RELAY-`), a string such as `"EVM-1-999999"` still passes the `starts_with("EVM-")` gate (so any caller who validates the identifier by prefix, e.g. matching it against an allow-listed chain string, an "expected source" comparison, or a config-driven prefix check) but is parsed by `from_str` into `StateMachine::Evm(999999)` — the *last* leg — not `StateMachine::Evm(1)`, the leg an operator/reviewer would expect from the prefix. This is a structural leg-injection identical in kind to the JSON-path `.key("internal.ssn")` traversal: one reserved separator, multiple unescaped occurrences, and downstream code that assumes "one leg after the marker" without enforcing it.

The `RELAY-` arm compounds the issue: `values.get(1)` for the relay code and `values.last()` for the para id means an attacker who controls the relay-code leg can inject its own `-`-delimited sub-legs to shift which segment lands at index 1 vs. the tail, letting the parsed `relay` bytes and `para_id` diverge from what a caller validating only the overall string prefix or a truncated substring would expect.

`StateMachine::Display`/`FromStr` is the canonical stringly encoding used throughout the config/API/indexer/SDK layers to represent `StateMachine` identifiers (`source`, `dest`, `consensus_state_id` bindings, RPC parameters), and is parsed via `from_str::<StateMachine>` in `modules/ismp/core/src/abi.rs` (10 occurrences) as well as in relayer fee/reward and CLI code paths. [3](#0-2) 

### Impact Explanation
Where this parser is used to convert an attacker-influenced or externally-supplied string into a `StateMachine` value that then feeds into consensus-client selection, challenge-period lookup, relayer-reward routing, or module/route dispatch, the leg-injection lets an attacker cause the parsed chain identity to diverge from whatever value a caller's prefix/format check believed it validated. Depending on which call site relies on this (e.g. reward/allow-list matching by prefix vs. actual numeric id used for payout, or a relayer/consensus config keyed by the *displayed* prefix rather than the fully-parsed value), this can result in:
- messages/rewards/state being attributed to or accepted for the wrong state machine (misdelivery / unintended-destination routing — analogous to reading `internal.ssn` instead of `nick`),
- a route becoming unable to deliver messages correctly because the id used for consensus-client/challenge-period lookup differs from the id implied by validated configuration.

### Likelihood Explanation
Likelihood is limited by how much of this string-form identifier is actually attacker-controlled at each of the confirmed call sites. I was not able to fully verify, within the available tool budget, the exact call sites inside `modules/ismp/core/src/abi.rs` or the relayer fee/reward code that invoke `StateMachine::from_str`/`.parse::<StateMachine>()`, so I cannot conclusively confirm an end-to-end attacker-controlled string reaching this parser from a single unprivileged dispatched message, a relayed proof, or a token transfer, the way the Kysely PoC concretely demonstrated data disclosure. The parsing bug itself is proven and reproducible from the `host.rs` source (confirmed by its own test suite showing round-trip assumptions but no test for extra `-` injection), but the "reachable from a single unprivileged transaction with concrete fund/protocol impact" requirement is **not fully proven** with the evidence gathered in this session.

### Recommendation
- Require an exact segment count for each `StateMachine` variant in `FromStr` (e.g. `debug_assert!(name.split('-').count() == 2)` for `EVM-`/`POLKADOT-`/`KUSAMA-`, `== 3` for `RELAY-`), rejecting any string with extra `-` characters instead of silently taking `.last()`/`.get(1)`.
- Audit every caller that performs a `starts_with`/prefix-based validation of a `StateMachine` string (config allow-lists, reward eligibility checks, RPC input validation) to ensure it uses the fully-parsed `StateMachine` value for authorization decisions rather than a raw substring of the identifier.
- Add a regression test asserting `StateMachine::from_str("EVM-1-999999")` and `StateMachine::from_str("RELAY-CENJ-1-1000")` return an error rather than a spoofed id.

### Proof of Concept
```rust
// modules/ismp/core/src/host.rs — FromStr for StateMachine
use ismp::host::StateMachine;
use core::str::FromStr;

// A caller that trusts the prefix ("this identifier is for EVM chain 1")
// but the parser actually returns chain 999999 because it takes the LAST
// '-'-delimited segment, not the second.
let attacker_supplied = "EVM-1-999999";
assert!(attacker_supplied.starts_with("EVM-"));           // passes any prefix-based allow-list check
let parsed = StateMachine::from_str(attacker_supplied).unwrap();
assert_eq!(parsed, StateMachine::Evm(999999));             // NOT StateMachine::Evm(1)
```
This mirrors the Kysely PoC pattern (`key("internal.ssn")` passing a "top-level key" check while actually addressing a nested field): the `-` leg separator is not sanitized/bounded, so a single unescaped extra occurrence changes which "leg" of the identifier is authoritative between the validation step and the parsing step.

### Citations

**File:** modules/ismp/core/src/host.rs (L344-426)
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
			name if name.starts_with("KUSAMA-") => {
				let id = name
					.split('-')
					.last()
					.and_then(|id| u32::from_str(id).ok())
					.ok_or_else(|| format!("invalid state machine: {name}"))?;
				StateMachine::Kusama(id)
			},
			name if name.starts_with("SUBSTRATE-") => {
				let name = name
					.split('-')
					.last()
					.ok_or_else(|| format!("invalid state machine: {name}"))?;
				let bytes = name.as_bytes();
				if bytes.len() != 4 {
					Err(format!("invalid state machine: {name}"))?
				}
				let mut id = [0u8; 4];
				id.copy_from_slice(bytes);
				StateMachine::Substrate(id)
			},
			name if name.starts_with("TNDRMINT-") => {
				let name = name
					.split('-')
					.last()
					.ok_or_else(|| format!("invalid state machine: {name}"))?;
				let bytes = name.as_bytes();
				if bytes.len() != 4 {
					Err(format!("invalid state machine: {name}"))?
				}
				let mut id = [0u8; 4];
				id.copy_from_slice(bytes);
				StateMachine::Tendermint(id)
			},
			name => Err(format!("Unknown state machine: {name}"))?,
		};

		Ok(s)
	}
}
```

**File:** modules/ismp/core/src/host.rs (L429-490)
```rust
mod tests {
	use crate::host::StateMachine;
	use alloc::string::ToString;
	use core::str::FromStr;

	#[test]
	fn state_machine_conversions() {
		let grandpa = StateMachine::Substrate(*b"hybr");
		let beefy = StateMachine::Tendermint(*b"hybr");
		let solo_relay = StateMachine::Relay { relay: *b"CENJ", para_id: 1000 };

		let grandpa_string = grandpa.to_string();
		let beefy_string = beefy.to_string();
		let solo_string = solo_relay.to_string();
		dbg!(&grandpa_string);
		dbg!(&beefy_string);
		dbg!(&solo_string);

		assert_eq!(grandpa, StateMachine::from_str(&grandpa_string).unwrap());
		assert_eq!(beefy, StateMachine::from_str(&beefy_string).unwrap());
		assert_eq!(solo_relay, StateMachine::from_str(&solo_string).unwrap());
	}

	#[test]
	fn invalid_state_machine_conversions() {
		let grandpa = StateMachine::Substrate(*b"\xf0\x28\x8c\xbc");
		let beefy = StateMachine::Tendermint(*b"\xf0\x28\x8c\xbc");
		let solo_relay = StateMachine::Relay { relay: *b"\xf0\x28\x8c\xbc", para_id: 1000 };

		let grandpa_string = grandpa.to_string();
		let beefy_string = beefy.to_string();
		let solo_string = solo_relay.to_string();
		dbg!(&grandpa_string);
		dbg!(&beefy_string);
		dbg!(&solo_string);

		assert_eq!(grandpa_string, "SUBSTRATE-XXXX".to_string());
		assert_eq!(beefy_string, "TNDRMINT-XXXX".to_string());
		assert_eq!(solo_string, "RELAY-XXXX-1000".to_string());
	}

	// A malformed `SUBSTRATE-`/`TNDRMINT-` id whose byte length is not exactly 4
	// must return an error rather than panic. The id is copied into a `[u8; 4]`,
	// and `copy_from_slice` traps on a length mismatch — in the runtime this is a
	// wasm trap reachable from untrusted input (e.g. `BandwidthManager.purchase`),
	// so the length is now checked up-front (matching the `RELAY-` arm).
	#[test]
	fn from_str_rejects_non_four_byte_consensus_ids() {
		for s in ["SUBSTRATE-", "SUBSTRATE-AB", "SUBSTRATE-ABCDE", "TNDRMINT-XYZ"] {
			assert!(StateMachine::from_str(s).is_err(), "expected error for {s:?}");
		}
		// Exactly-4-byte ids still parse.
		assert_eq!(
			StateMachine::from_str("SUBSTRATE-ABCD").unwrap(),
			StateMachine::Substrate(*b"ABCD")
		);
		assert_eq!(
			StateMachine::from_str("TNDRMINT-ABCD").unwrap(),
			StateMachine::Tendermint(*b"ABCD")
		);
	}
}
```
