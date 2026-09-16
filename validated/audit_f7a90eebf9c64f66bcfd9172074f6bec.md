### Title
Attacker-controlled `StateMachine::Substrate`/`Tendermint`/`Relay` bytes containing `-` corrupt the `Display`/`FromStr` and SDK/indexer string round-trip used for routing and accounting - ([File: modules/ismp/core/src/host.rs])

### Summary
`ismp::host::StateMachine` renders `Substrate`, `Tendermint`, and `Relay` variants as delimited strings (`"SUBSTRATE-{id}"`, `"TNDRMINT-{id}"`, `"RELAY-{relay}-{para_id}"`) using the raw, attacker-influenced 4-byte chain identifier interpolated directly into a `-`-delimited format, and multiple downstream consumers (Rust `FromStr`, the TypeScript SDK's `parseStateMachineId`/`getStateId`, and the indexer's `formatChain`/`extractStateMachineIdFromSubstrateEventData`) parse that same string by naively splitting on `-`. A 4-byte id is valid UTF-8 and may legally contain the `0x2D` (`-`) byte, so a user who controls a `dest`/`source` state machine id for a dispatched request (e.g. `StateMachine.substrate(bytes)` in Solidity, or any GetRequest/PostRequest `dest`) can choose bytes such that the produced string carries extra `-` separated segments, corrupting parsers that assume exactly one delimiter and silently truncate or misparse the value.

### Finding Description
`StateMachine`'s `Display` implementation formats the raw 4-byte id inline with `-` as separator without escaping: [1](#0-0) 

The reciprocal `FromStr` implementation naively `split('-')`s the string and takes `.last()` (or a fixed slice), which is only correct if the embedded id contains no `-` byte: [2](#0-1) 

The 4-byte id is not validated to exclude ASCII control/delimiter characters — the code already went through one hardening pass (documented in a nearby test) that fixed a panic on non-4-byte inputs "reachable from untrusted input (e.g. `BandwidthManager.purchase`)", confirming this id is attacker-reachable through normal user calls, but that fix did not address delimiter-content corruption: [3](#0-2) 

The same fragile assumption is duplicated across the stack that consumes this Display-formatted string:
- SDK `parseStateMachineId` splits on the first `-` only and does not reject additional dashes in the value: [4](#0-3) 
- SDK `substrate.ts`'s `convertStateMachineIdToEnum`/`getStateId`-style helpers split on `-`: [5](#0-4) 
- Indexer `getStateId` destructures only the first two `-`-separated segments, silently dropping everything after the second dash: [6](#0-5) 
- Indexer event parsing similarly re-concatenates without checking for embedded delimiters: [7](#0-6) 

On the dispatch side, the destination/source state-machine identifier for a request is user-supplied per-request (e.g. `StateMachine.substrate(bytes memory id)` in Solidity, taking arbitrary caller bytes) and is decoded on-chain into `StateMachine::Substrate([u8;4])`/`Tendermint([u8;4])` without any restriction that the 4 bytes must be printable/non-delimiter characters. Any code path that later renders that `StateMachine` to a string (RPC parameters such as `ismp_queryChallengePeriod`, relayer configuration matching, the indexer, or SDK fee/config lookups keyed by the string form) will then silently truncate or misparse the identifier, because none of the consumers reject embedded `-` bytes in the id portion.

This mirrors the underlying bug class in the referenced NATS advisory: untrusted data that is embedded, unescaped, into a delimiter-based text protocol and later re-parsed by a downstream component that assumes the delimiter cannot appear inside a field, causing the downstream parser to see unintended "extra fields."

### Impact Explanation
The truncation/misparse silently produces the *wrong* state-machine identifier being used by the SDK/indexer/relayer for downstream string-keyed lookups (fee-token decimals, config-by-chain-id lookups, accumulated-fee records, RPC parameters). Concretely this can:
- Cause `parseStateMachineId`/`getStateId`-driven config lookups (`getIntentGatewayAddress`, `getFeeTokenDecimals`, per-chain RPC/fee config) to resolve to a truncated/incorrect identifier, which for chains that share a truncated prefix can silently point requests, fee-token pricing, or fee accounting at the wrong chain's configuration — a form of message misdelivery / fund-accounting corruption rather than mere validation failure.
- Cause the Rust `FromStr` round-trip to reject a legitimately-encoded chain id (since `.split('-').last()` yields a fragment whose length no longer matches the expected 4 bytes), so a state machine whose id happens to contain `-` can never be correctly re-parsed by RPC/relayer tooling that goes through the string form, effectively making a route to that state machine undeliverable.

Because the id is attacker-chosen per-dispatched-request (not admin-configured), this is reachable by any unprivileged user dispatching a cross-chain request with a crafted `dest`/`source` state-machine identifier.

### Likelihood Explanation
High reachability (any user dispatching a `GetRequest`/`PostRequest` picks `dest`) but the concrete "wrong chain" collision requires the corrupted string to coincidentally match another legitimate/registered chain-id string used elsewhere, or requires an operator/relayer to feed the Display-string form back through a splitting parser (which multiple SDK/indexer code paths do). The presence of an already-fixed adjacent panic bug in the same code, explicitly called out as "reachable from untrusted input," indicates this identifier is a known-hostile input surface that has not been fully hardened against delimiter injection.

### Recommendation
- Reject (or percent/hex-escape) any `Substrate`/`Tendermint`/`Relay` 4-byte id containing the `-` delimiter (or restrict to a safe alphanumeric charset) at the point the id is first decoded from untrusted bytes (`StateMachine` construction / dispatch entry points), not just at `FromStr`.
- Make `Display`/`FromStr` use a delimiter-safe encoding (e.g., hex-encode the raw id bytes instead of interpreting them as UTF-8 and splicing with `-`), and update the TypeScript SDK and indexer helpers (`parseStateMachineId`, `getStateId`, `convertStateMachineIdToEnum`, `extractStateMachineIdFromSubstrateEventData`, `formatChain`) to use the same unambiguous encoding, splitting on the first `-` only and validating there are no unexpected extra segments.
- Add a regression test asserting that ids containing `-` (and other non-alphanumeric bytes) are rejected consistently across the Rust and TypeScript implementations, mirroring the existing 4-byte-length regression test.

### Proof of Concept
1. A user dispatches a `GetRequest`/`PostRequest` (e.g. via `IDispatcher(_host).dispatch(...)` in an EVM app, or the pallet-hyper-fungible-token `send`) specifying `dest = StateMachine.substrate(bytes4(0x41422D43))` — i.e. raw id bytes `b"AB-C"`, all valid printable ASCII/UTF-8.
2. On the Rust side this decodes to `StateMachine::Substrate([0x41,0x42,0x2D,0x43])` (`"AB-C"`), and `Display` produces the string `"SUBSTRATE-AB-C"`. [8](#0-7) 
3. Any consumer that parses this string by splitting on `-` and taking a fixed segment count/position (Rust `FromStr`'s `.split('-').last()`, the SDK's `parseStateMachineId`'s `stateMachineId.split("-")`, or the indexer's `getStateId`'s `id.split("-")` destructuring into exactly `[type, value]`) either:
   - fails length validation on the Rust side and rejects re-parsing this legitimate identifier (`"C"` has length 1, not 4), making this state machine undeliverable through any tooling that round-trips via the string form, or
   - silently drops the tail (`"-C"`) on the SDK/indexer side, yielding the wrong chain identifier `"AB"` used for fee-token/config lookups. [9](#0-8) [6](#0-5) 

**Note on confidence**: I was not able to trace, within the available indexing, a concrete instance where the corrupted/truncated string collides with another real chain's registered identifier to cause direct fund theft (the config maps in `sdk/packages/sdk/src/configs/chain.ts` use fixed, short numeric or known-string suffixes, making an exact collision unlikely but not provably impossible for all deployed Substrate/Tendermint state machines). The clearest, most defensible impact is the "route unable to deliver messages" / accounting-corruption class rather than a proven direct fund-theft primitive; a full confirmation would require tracing every relayer/indexer/config code path that consumes the `Display`-derived string for a security-relevant decision, which exceeds what the current index exposes. If this needs deeper verification, a Devin session with full repo access could trace all such consumers exhaustively.

### Citations

**File:** modules/ismp/core/src/host.rs (L313-342)
```rust
impl Display for StateMachine {
	fn fmt(&self, f: &mut core::fmt::Formatter<'_>) -> core::fmt::Result {
		let str = match self {
			StateMachine::Evm(id) => {
				format!("EVM-{id}")
			},
			StateMachine::Polkadot(id) => format!("POLKADOT-{id}"),
			StateMachine::Kusama(id) => format!("KUSAMA-{id}"),
			// Invalid byte sequence will result in a default state machine id rendering the request
			// invalid and undeliverable
			StateMachine::Substrate(id) => {
				format!(
					"SUBSTRATE-{}",
					String::from_utf8(id.to_vec()).unwrap_or("XXXX".to_string())
				)
			},
			// Invalid byte sequence will result in a default state machine id rendering the request
			// invalid and undeliverable
			StateMachine::Tendermint(id) =>
				format!("TNDRMINT-{}", String::from_utf8(id.to_vec()).unwrap_or("XXXX".to_string())),
			// Invalid byte sequence will result in a default state machine id rendering the request
			// invalid and undeliverable
			StateMachine::Relay { relay, para_id } => format!(
				"RELAY-{}-{para_id}",
				String::from_utf8(relay.to_vec()).unwrap_or("XXXX".to_string())
			),
		};
		write!(f, "{}", str)
	}
}
```

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

**File:** modules/ismp/core/src/host.rs (L470-489)
```rust
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
```

**File:** sdk/packages/sdk/src/utils.ts (L134-187)
```typescript
export function parseStateMachineId(stateMachineId: string): {
	stateId: { Evm?: number; Substrate?: HexString; Polkadot?: number; Kusama?: number }
} {
	const [type, value] = stateMachineId.split("-")

	if (!type || !value) {
		throw new Error(
			`Invalid state machine ID format: ${stateMachineId}. Expected format like "EVM-97" or "SUBSTRATE-cere"`,
		)
	}

	const stateId: { Evm?: number; Substrate?: HexString; Polkadot?: number; Kusama?: number } = {}

	switch (type.toUpperCase()) {
		case "EVM": {
			const evmChainId = Number.parseInt(value, 10)
			if (Number.isNaN(evmChainId)) {
				throw new Error(`Invalid EVM chain ID: ${value}. Expected a number.`)
			}
			stateId.Evm = evmChainId
			break
		}

		case "SUBSTRATE": {
			// Convert the string to hex-encoded UTF-8 bytes
			const bytes = Buffer.from(value, "utf8")
			stateId.Substrate = `0x${bytes.toString("hex")}` as HexString
			break
		}

		case "POLKADOT": {
			const polkadotChainId = Number.parseInt(value, 10)
			if (Number.isNaN(polkadotChainId)) {
				throw new Error(`Invalid Polkadot chain ID: ${value}. Expected a number.`)
			}
			stateId.Polkadot = polkadotChainId
			break
		}

		case "KUSAMA": {
			const kusamaChainId = Number.parseInt(value, 10)
			if (Number.isNaN(kusamaChainId)) {
				throw new Error(`Invalid Kusama chain ID: ${value}. Expected a number.`)
			}
			stateId.Kusama = kusamaChainId
			break
		}

		default:
			throw new Error(`Unsupported chain type: ${type}. Expected one of: EVM, SUBSTRATE, POLKADOT, KUSAMA.`)
	}

	return { stateId }
}
```

**File:** sdk/packages/sdk/src/chains/substrate.ts (L598-608)
```typescript
export function convertStateMachineIdToEnum(id: string): IStateMachine {
	let [tag, value]: any = id.split("-")
	tag = capitalize(tag)
	if (["Evm", "Polkadot", "Kusama"].includes(tag)) {
		value = Number.parseInt(value)
	} else {
		value = Array.from(toBytes(value))
	}

	return { tag, value }
}
```

**File:** sdk/packages/indexer/src/utils/state-machine.helper.ts (L243-264)
```typescript
export const getStateId = (id: string) => {
	const [type, value] = id.split("-")
	const tag = getStateMachineTag(type)

	switch (tag) {
		case "Evm":
		case "Polkadot":
		case "Kusama":
			return {
				tag,
				value: Number(value),
			}
		case "Substrate":
		case "Tendermint":
			return {
				tag,
				value: Array.from(new TextEncoder().encode(value)),
			}
		default:
			throw new Error(`Unknown state machine type: ${type}`)
	}
}
```

**File:** sdk/packages/indexer/src/utils/substrate.helpers.ts (L48-63)
```typescript
		switch (main_key) {
			case "EVM":
				return "EVM-".concat(value)
			case "POLKADOT":
				return "POLKADOT-".concat(value)
			case "KUSAMA":
				return "KUSAMA-".concat(value)
			case "SUBSTRATE":
				return "SUBSTRATE-".concat(value)
			case "TENDERMINT":
				return "TENDERMINT-".concat(value)
			default:
				throw new Error(
					`Unknown state machine ID ${main_key} encountered in extractStateMachineIdFromSubstrateEventData. `,
				)
		}
```
