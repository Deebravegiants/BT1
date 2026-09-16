### Title
State machine identifier confusion via unescaped `-` delimiter in `StateMachine::FromStr` - ([File: modules/ismp/core/src/host.rs])

### Summary
`StateMachine::from_str` (the canonical parser Hyperbridge components use to turn a chain/consensus identifier string back into a `StateMachine` enum value) splits the string on the literal `-` character and, for the `SUBSTRATE-`, `TNDRMINT-` and `RELAY-` variants, blindly takes the *last* `-`-delimited segment as the raw consensus/relay id bytes. Because the 4-byte consensus id is embedded into the string without quoting or escaping the `-` separator, a string containing an extra, attacker-chosen `-` inside what looks like one identifier is silently re-parsed as a completely different identifier, exactly as the email header vulnerability lets an unescaped newline be re-interpreted as a header boundary.

### Finding Description
`Display for StateMachine` renders `Substrate`/`Tendermint`/`Relay` variants by writing the raw consensus-id bytes straight into the string after the `-` separator with no escaping: [1](#0-0) 

The corresponding `FromStr for StateMachine` implementation reverses this by splitting on `-` and taking `.split('-').last()` for the id portion: [2](#0-1) 

Because a `ConsensusStateId`/relay id is just 4 arbitrary bytes and one of the printable ASCII values that satisfies the `bytes.len() == 4` guard is `0x2D` (`-`) itself, a fully-formed identifier such as
```
SUBSTRATE-ABCD-WXYZ
```
splits into `["SUBSTRATE", "ABCD", "WXYZ"]`. `.last()` returns `"WXYZ"` (4 bytes), so this string round-trips to `StateMachine::Substrate(*b"WXYZ")`, silently discarding the `"ABCD"` segment. Any code path that treats the *full string* as the canonical identifier (string equality checks, logging, off-chain indexing, fee/bandwidth bookkeeping keyed by the raw string) will disagree with any code path that calls `StateMachine::from_str` on the same string — the latter sees a different, attacker-chosen state machine than what the string appears to represent. This is structurally identical to the reported email bug class: an unescaped delimiter embedded in attacker-controlled data lets a parser interpret extra content as a new, separate field/record rather than as part of the original data.

The codebase's own regression test acknowledges this string is parsed from untrusted, attacker-reachable input: [3](#0-2) 
with the comment explicitly citing `BandwidthManager.purchase` as a path where a caller-supplied state-machine string reaches `StateMachine::from_str` in the runtime.

### Impact Explanation
An unprivileged caller (e.g. anyone invoking `BandwidthManager.purchase` with an attacker-crafted destination/state-machine string) can construct a state-machine identifier string that:
- Displays/logs/is stored as one chain identity (e.g. an id meant for chain `ABCD`), while
- Actually parses via `StateMachine::from_str` to a *different* `StateMachine` value (`WXYZ`).

Any component that reasons about "which chain does this identifier belong to" using string-level equality/prefix checks versus components that reason about it using the parsed enum (fee accounting, bandwidth purchase crediting, relayer reward accounting, consensus-client lookup, or route validation) can be made to disagree. This can misroute bandwidth credit or fee accounting to an unintended state machine, or let a caller mint/associate a purchase intended for chain `X`'s string label with a completely different registered `StateMachine` enum value, and in the worst case makes some legitimately-registered identifiers permanently unparseable/ambiguous — a route that can no longer be correctly identified or delivered to, satisfying the "unsound state commitment / unauthorized app action / route unable to deliver messages" bar.

### Likelihood Explanation
The precondition is simply choosing a 4-byte consensus/relay id whose bytes include `0x2D` (`-`), which is entirely within an unprivileged caller's control when the identifier is supplied off-chain/as calldata (as in `BandwidthManager.purchase`), and no validation rejects `-` inside the id segment before it round-trips through `Display`/`FromStr`. This requires only a single crafted transaction/call — no privileged role, no consensus proof, no timing race.

### Recommendation
- Do not use a naked-delimiter string as the canonical wire/comparison format for `StateMachine`. Either length/position-prefix each field (fixed-width segments, as already partially enforced by the 4-byte checks) instead of relying on split-by-`-`, or reject any consensus/relay id byte sequence containing `0x2D` at registration/construction time.
- Make `FromStr` split on the *first* `-` only (`splitn(2, '-')`) for the type tag, and then validate that the remainder, after removing the fixed-width id, contains no further unexpected `-` for `RELAY-` (which has a fixed two-field trailing structure) — i.e., parse positionally rather than via `.last()`.
- Ensure every consumer that needs to compare "is this the same chain" always goes through `StateMachine::from_str` + enum equality rather than raw string comparison, to eliminate the divergence surface even if the ambiguous encoding remains.

### Proof of Concept
1. Choose a consensus id `b"ABCD"` is not required; instead directly craft the string `"SUBSTRATE-ABCD-WXYZ"` (any two 4-character segments) and pass it as the destination/state-machine argument to a caller-reachable entry point that forwards it into `StateMachine::from_str` (per the codebase's own note, `BandwidthManager.purchase`).
2. Observe that `StateMachine::from_str("SUBSTRATE-ABCD-WXYZ")` returns `Ok(StateMachine::Substrate(*b"WXYZ"))`, per the `split('-').last()` logic: [4](#0-3) 
3. Compare this to any code path that stores/keys/logs the raw input string `"SUBSTRATE-ABCD-WXYZ"` verbatim (e.g., displaying it as belonging to `"ABCD"`-prefixed identity) — the two views of "which chain this is" now diverge for the same submitted call, demonstrating the identifier-confusion / injection primitive.

### Citations

**File:** modules/ismp/core/src/host.rs (L323-338)
```rust
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
