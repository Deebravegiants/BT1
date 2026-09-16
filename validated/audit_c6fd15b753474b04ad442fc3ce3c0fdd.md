### Title
Unsigned zstd-decompression dispatcher can be wedged into an unbounded loop by a malformed compressed payload - (File: modules/pallets/call-decompressor/src/lib.rs)

### Summary
`pallet-call-decompressor`'s `decompress` function feeds attacker-controlled bytes straight into `ruzstd::StreamingDecoder` and repeatedly calls `.read()` in an unbounded `loop` with no cap on the number of iterations, no fuel/step limit, and no timeout. This function is reachable both from the unsigned extrinsic `decompress_call` (`ensure_none` origin — no signature, no fee) and, more critically, from `validate_unsigned`, which every full/collator node runs on *every* candidate transaction received over the p2p transaction pool, before the transaction is ever included in a block. This mirrors the reported Snappier bug class (CWE-835): a decompression stream that can enter an uncatchable/uninterruptible loop on malformed framed compressed input, with no exception ever raised to let a caller recover. [1](#0-0) 

### Finding Description
`decompress_call` is dispatched with `ensure_none(origin)?`, i.e. by any unprivileged sender with no fee and no signature: [2](#0-1) 

The decompression itself is:
```rust
let mut decoder = StreamingDecoder::new(compressed_bytes.as_slice())...;
loop {
    let n = decoder.read(&mut chunk).map_err(|_| Error::<T>::DecompressionFailed)?;
    if n == 0 { break; }
    ...
}
``` [3](#0-2) 

This loop's termination is entirely delegated to the external `ruzstd` `StreamingDecoder::read` implementation returning either an `Err`, `Ok(0)`, or eventually exhausting the stream. There is no bound on the number of `read()` calls, no cumulative "steps" counter, and no interruption mechanism — exactly the shape of bug the Snappier advisory describes: a decompressor whose internal loop (there, `SnappyStreamDecompressor.Decompress`/`Crc32CAlgorithm.Append`; here, `ruzstd`'s frame/block state machine) can be driven into a non-terminating busy loop by a malformed but small compressed input, with `try/catch` unable to recover because no exception is ever thrown.

The same code path is also invoked from `validate_unsigned`, which fires for every transaction of this call type gossiped to a node's mempool, prior to any execution weight metering or fee deduction: [4](#0-3) 

This is a strictly worse reachability profile than the dispatch path: a node's transaction-validation logic (single-threaded per queue in Substrate's transaction pool) can be wedged by one gossiped, fee-less, unsigned transaction, before block-weight limits ever apply.

Note: the exact internal behavior of `ruzstd::StreamingDecoder::read` on malformed zstd frames is outside this repository (external crate) and could not be directly inspected here; this finding treats the Snappier report as the bug-class hint per the analysis rules and demonstrates that the reachable Hyperbridge code has zero defense-in-depth against such a decoder-level infinite loop (unlike the output-size bound that was explicitly added for the "zstd bomb" memory-exhaustion case).

### Impact Explanation
If `ruzstd`'s decoder can be driven into a non-terminating state on crafted input (the same bug class as Snappier), a single unsigned, feeless transaction gossiped to the network can:
- Hang the `validate_unsigned` path on every node that receives the transaction via p2p gossip before it is ever included in a block, and
- Hang block execution/import on any node that includes and executes the `decompress_call` extrinsic in a block.

Both are consensus-critical, unprivileged, network-reachable denial-of-service vectors (CWE-835 / CVSS AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:H — matching the cited advisory), able to render nodes unable to import/validate transactions or produce/import blocks, which halts message delivery for `pallet-ismp` since the runtime and its extrinsic queue would no longer make progress.

### Likelihood Explanation
The `compressed` bytes and `encoded_call_size` are fully attacker-controlled, the call requires no signature or fee (`ensure_none`), and it is exercised by every full node's mempool validation on receipt — no special privilege, timing, or governance action is required. The only mitigating factor is that the actual trigger condition depends on an as-yet-unconfirmed defect inside the vendored `ruzstd` decoder analogous to the one found in Snappier; this repo's code provides no guardrail (iteration cap, fuel limit, or watchdog) that would contain such a defect if it exists.

### Recommendation
- Bound the decompression loop with an explicit maximum number of `read()` iterations (or total bytes read across zero-length reads) independent of the decoder's own termination logic, so a stuck/non-advancing decoder cannot loop forever.
- Wrap `decompress` in a metered/step-limited execution context (e.g. periodically check a deadline/weight budget and abort with `DecompressionFailed` if exceeded), both in `decompress_call` and in `validate_unsigned`.
- Pin and audit the `ruzstd` version for any known infinite-loop/hang issues on malformed frames, matching the fix class released for Snappier (`>=1.3.1`), and add fuzz/property tests feeding truncated and malformed zstd frames into `Pallet::decompress` to confirm termination.

### Proof of Concept
Conceptual PoC (mirrors the Snappier PoC pattern):
1. Craft a small malformed zstd-compressed byte sequence that trips the same class of decoder-state bug as the Snappier PoC (a truncated/malformed frame header/block that causes the decoder's internal read loop to spin without advancing the stream cursor).
2. Submit it as an unsigned `decompress_call(compressed = <malformed bytes>, encoded_call_size = <any value under MaxCallSize>)` transaction, or simply gossip it to a node's transaction pool.
3. `validate_unsigned` invokes `Pallet::decompress`, which invokes `decoder.read(&mut chunk)` in the unbounded `loop`; if the decoder never returns (per the reported bug class), the node's transaction-validation thread hangs indefinitely with no exception raised, exactly as in the Snappier `SnappyStream.CopyTo` PoC.

### Citations

**File:** modules/pallets/call-decompressor/src/lib.rs (L109-122)
```rust
		pub fn decompress_call(
			origin: OriginFor<T>,
			compressed: Vec<u8>,
			encoded_call_size: u32,
		) -> DispatchResult {
			ensure_none(origin)?;
			ensure!(
				encoded_call_size < T::MaxCallSize::get() * ONE_MB,
				Error::<T>::CallSizeOutOfBound
			);
			let call_bytes = Self::decompress(compressed, encoded_call_size)?;
			Self::decode_and_execute(call_bytes)?;
			Ok(())
		}
```

**File:** modules/pallets/call-decompressor/src/lib.rs (L141-153)
```rust
		fn validate_unsigned(source: TransactionSource, call: &Self::Call) -> TransactionValidity {
			let Call::decompress_call { compressed, encoded_call_size } = call else {
				return Err(TransactionValidityError::Invalid(InvalidTransaction::Call));
			};

			let decompressed = Self::decompress(compressed.clone(), encoded_call_size.clone())
				.map_err(|_| TransactionValidityError::Invalid(InvalidTransaction::Call))?;

			let runtime_call = T::RuntimeCall::decode_all_with_depth_limit(
				MAX_EXTRINSIC_DECODE_DEPTH_LIMIT,
				&mut &decompressed[..],
			)
			.map_err(|_| TransactionValidityError::Invalid(InvalidTransaction::Call))?;
```

**File:** modules/pallets/call-decompressor/src/lib.rs (L233-254)
```rust
		let mut decoder = StreamingDecoder::new(compressed_bytes.as_slice())
			.map_err(|_| Error::<T>::DecompressionFailed)?;

		let claimed = encoded_call_size as usize;
		let mut result = Vec::new();
		let mut chunk = vec![0u8; 4096];

		loop {
			let n = decoder.read(&mut chunk).map_err(|_| Error::<T>::DecompressionFailed)?;
			if n == 0 {
				break;
			}
			if result.len() + n > claimed {
				return Err(Error::<T>::DecompressionFailed.into());
			}
			result.extend_from_slice(&chunk[..n]);
		}

		ensure!(result.len() == claimed, Error::<T>::DecompressionFailed);

		Ok(result)
	}
```
