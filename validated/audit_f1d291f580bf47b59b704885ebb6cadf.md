Based on my investigation, `IntentGatewayV2.sol` no longer calls `recordSpread` (confirmed by grep: `priceOracle`/`recordSpread` do not appear in `evm/src/apps/IntentGatewayV2.sol` or `intentsv2/IntentsBase.sol` anymore, only in `sdk/packages/core/contracts/apps/IntentGatewayV2.sol`'s legacy interface/struct field and in `VWAPOracle.sol` itself). This matches the changelog I found documenting the exact fix.

### Title
Historical: Unvalidated `order.inputs`/`options.outputs` fed into `VWAPOracle.recordSpread` critical price-state — already remediated - (File: `evm/src/utils/VWAPOracle.sol`)

### Summary
An analog of the reported bug class did exist in this codebase: `IntentGatewayV2.fillOrder` used to call `IIntentPriceOracle.recordSpread(commitment, order.inputs, options.outputs)` passing the filler-supplied `options.outputs` and the order's `inputs` **verbatim** into `VWAPOracle.recordSpread`, which used them to update a cumulative, volume-weighted global price/spread state (`_tokenSpreads`) — mirroring the FlatcoinVault pattern of an authorized-but-unverified caller pushing untrusted pricing data into global accounting state.

### Finding Description
`VWAPOracle.recordSpread` [1](#0-0)  is `restrict`ed only to `_intentGateway`, i.e. it trusts whatever `inputs`/`outputs` amounts the gateway forwards, and uses them directly to compute `spreadBps` and update `_tokenSpreads[...].weightedSpreadSum`/`totalVolume`, a VWAP-style global price state consumed via `spread()` [2](#0-1) . Per the project's own audit changelog, `fillOrder` "passed `order.inputs` and `options.outputs` to a stateful oracle verbatim, and neither is validated against anything that costs the caller money — the escrow lives on the source chain and is never consulted on the destination side," which is precisely the "unverified external price feeding a critical global-state update" bug class from the FlatcoinVault report. [3](#0-2) 

### Impact Explanation
Had this call still existed, a filler on the destination chain could declare an arbitrary `options.outputs` amount (not the amount they actually transferred, since it isn't checked against the escrow on the source chain) to skew the VWAP-tracked spread for a token pair arbitrarily — poisoning any downstream logic (filler reputation/pricing/fee decisions) that consults `IIntentPriceOracle.spread()`.

### Likelihood Explanation
This is a historical/patched issue, not a currently reachable path: the `recordSpread` call was removed from `IntentGatewayV2.fillOrder` (confirmed by grep — no `recordSpread`/`priceOracle` references remain in `evm/src/apps/IntentGatewayV2.sol` or `IntentsBase.sol`), per the security-audit-driven fix documented in the changelog. `VWAPOracle.recordSpread` itself remains defined and still gated to `_intentGateway`, but nothing in the current `IntentGatewayV2` calls it. `Params.priceOracle` field was deliberately left in the storage layout only to avoid an upgradeable-proxy storage-shift, not because the oracle is still wired in. [4](#0-3) 

### Recommendation
No action required on the live path — already fixed by removing the `recordSpread` call from `fillOrder`. If `VWAPOracle` is ever reintegrated (e.g. a future gateway version resumes calling `recordSpread`), the amounts recorded must be tied to values that actually cost the caller money (e.g. verified transfer amounts / escrow-release amounts) rather than filler-declared `outputs`, or the oracle should be removed entirely since it is dead code in the current gateway.

### Proof of Concept
Not applicable — the vulnerable call path no longer exists in the current `IntentGatewayV2.sol`/`IntentsBase.sol`. The only remaining evidence is the still-present, but now-unreachable, `VWAPOracle.recordSpread` function [1](#0-0)  and the audit changelog documenting the original vulnerable flow and its removal. [5](#0-4) 

Given that the concrete reachable path has been remediated and I found no other currently-reachable analog (EvmHost/consensus-client state updates all go through proof verification before storage writes, e.g. `storeStateMachineCommitment` is only called after `verify_consensus`/handler validation [6](#0-5) , and relayer fee accumulation requires state-proof verification against a committed root before crediting fees [7](#0-6) ), I cannot confirm a currently exploitable, in-scope analog beyond this already-patched one.

### Citations

**File:** evm/src/utils/VWAPOracle.sol (L141-147)
```text
    function spread(bytes memory sourceChain, address token) external view returns (int256) {
        bytes32 chainHash = keccak256(sourceChain);
        CumulativeSpreadData memory data = _tokenSpreads[chainHash][token];
        if (data.totalVolume == 0) return 0;

        return data.weightedSpreadSum / int256(data.totalVolume);
    }
```

**File:** evm/src/utils/VWAPOracle.sol (L170-216)
```text
    function recordSpread(
        bytes32 commitment,
        bytes memory sourceChain,
        TokenInfo[] calldata inputs,
        TokenInfo[] calldata outputs
    ) external restrict(_intentGateway) {
        // Validate inputs and outputs have the same length
        if (inputs.length != outputs.length || inputs.length == 0) {
            return;
        }

        bytes32 sourceChainHash = keccak256(sourceChain);
        uint256 tokensLen = inputs.length;
        for (uint256 i = 0; i < tokensLen; i++) {
            address inputToken = address(uint160(uint256(inputs[i].token)));
            address outputToken = address(uint160(uint256(outputs[i].token)));

            // Get decimals for input token from storage (remote chain)
            // Native tokens (address(0)) use 18 decimals
            uint8 inputDecimals = inputToken == address(0) ? 18 : _tokenDecimals[sourceChainHash][inputToken];
            if (inputDecimals == 0) continue; // Skip if decimals not configured

            // Get decimals for output token directly from contract (local chain)
            // Native tokens (address(0)) use 18 decimals
            uint8 outputDecimals = outputToken == address(0) ? 18 : IERC20Metadata(outputToken).decimals();

            // Normalize both amounts to 18 decimals for comparison
            uint256 inputAmountNormalized = _normalizeAmount(inputs[i].amount, inputDecimals);
            uint256 outputAmountNormalized = _normalizeAmount(outputs[i].amount, outputDecimals);

            // Calculate spread for this token: (output - input) / input * 10000
            // Positive spread = filler provided more tokens (good for user)
            // Negative spread = filler provided fewer tokens (filler captured spread)
            int256 spreadBps = 0;
            if (inputAmountNormalized > 0) {
                int256 amountDiff = int256(outputAmountNormalized) - int256(inputAmountNormalized);
                spreadBps = (amountDiff * int256(BPS_DENOMINATOR)) / int256(inputAmountNormalized);
            }

            // Update cumulative spread data for this token (weighted by volume)
            int256 weightedSpread = spreadBps * int256(inputAmountNormalized);
            _updateCumulativeSpread(_tokenSpreads[sourceChainHash][inputToken], weightedSpread, inputAmountNormalized);

            // Emit event for each token
            emit SpreadRecorded(commitment, outputToken, spreadBps);
        }
    }
```

**File:** sdk/packages/sdk/docs/ai/changelog/2026-08-27-filloptions-carries-a-validuntil-and-fillorder-has-two-shapes.md (L1-34)
```markdown
# 2026-08-27 — `FillOptions` carries a `validUntil`, and `fillOrder` has two shapes

`FillOptions` gained `validUntil` (a block number; `0n` means unbounded), enforced by `fillOrder`, which now reverts
`FillExpired` past it. Adding a field changes the enclosing function's selector, so `fillOrder` exists in two
incompatible shapes — `0x5cfb1ea5` (v1) and `0xa5470064` (v2) — and gateways upgrade per chain, so both are on the
wire at once.

New `protocols/intents/fillOrderCodec.ts` owns that: `getFillOptionsVersion` reads the gateway's ERC-1967
implementation slot and matches the address against a set of known pre-`validUntil` implementations, defaulting to
v2; `encodeFillOrder` emits the matching shape and `decodeFillOrder` reads either. There is no version getter on
the contract — EIP-1967 has no version field either, and the implementation address is the value the proxy already
updates on upgrade. `GasEstimator` encodes through it so estimates do not revert on a missing function; `BidManager` and
`phantom-aggregation.extractFillData` decode through it so bids built against an older gateway are still priced in
rather than dropped.

Why the field exists: a solver bidding through the coprocessor signs this calldata and then has no further say in
when it is used. The order's `deadline` is placer-chosen with no ceiling, retracting the bid on Hyperbridge does not
reach the destination chain, and the placer holds the session key — so a signed bid stayed executable indefinitely
and was taken up only once the rate had moved against the solver. `validUntil` rides in the calldata, which
`userOpHash` already covers, so it is tamper-proof without touching the signature format.

`fillOrder` also no longer calls `IIntentPriceOracle.recordSpread`. It passed `order.inputs` and `options.outputs`
to a stateful oracle verbatim, and neither is validated against anything that costs the caller money — the escrow
lives on the source chain and is never consulted on the destination side. `Params.priceOracle` is left in place
because removing a field from a storage struct behind an upgradeable proxy shifts the layout.

Found by the scheduled IntentGateway/Simplex security audit.

Files: `src/protocols/intents/fillOrderCodec.ts` (new), `src/protocols/intents/GasEstimator.ts`,
`src/protocols/intents/BidManager.ts`, `src/protocols/intents/phantom-aggregation.ts`,
`src/protocols/intents/index.ts`, `src/abis/IntentGatewayV2.ts`, `src/types/index.ts`,
`src/tests/fillOrderCodec.test.ts` (new), `src/tests/phantomAggregation.test.ts`, plus
`evm/src/apps/IntentGatewayV2.sol`, `evm/src/apps/intentsv2/IntentsBase.sol` and
`sdk/packages/core/contracts/apps/IntentGatewayV2.sol`.
```

**File:** modules/ismp/core/src/handlers/consensus.rs (L41-70)
```rust
	let (new_state, intermediate_states) = consensus_client.verify_consensus(
		host,
		msg.consensus_state_id,
		trusted_state,
		msg.consensus_proof,
	)?;
	host.store_consensus_state(msg.consensus_state_id, new_state)?;
	let timestamp = host.timestamp();
	host.store_consensus_update_time(msg.consensus_state_id, timestamp)?;
	let mut state_updates = vec![];
	for (id, mut commitment_heights) in intermediate_states {
		commitment_heights.sort_unstable_by(|a, b| a.height.cmp(&b.height));
		let previous_latest_height = host.latest_commitment_height(id)?;
		let mut last_commitment_height = None;
		for commitment_height in commitment_heights.iter() {
			let state_height = StateMachineHeight { id, height: commitment_height.height };

			// Only allow heights greater than latest height
			if previous_latest_height > commitment_height.height {
				continue;
			}

			// Skip duplicate states
			if host.state_machine_commitment(state_height).is_ok() {
				continue;
			}

			last_commitment_height = Some(state_height);
			host.store_state_machine_commitment(state_height, commitment_height.commitment)?;
			host.store_state_machine_update_time(state_height, host.timestamp())?;
```

**File:** modules/pallets/relayer/src/accumulate.rs (L213-236)
```rust
	pub fn verify_withdrawal_proof(
		state_machine: &dyn ismp::consensus::StateMachineClient,
		proof: &Proof,
		keys: Vec<Vec<u8>>,
	) -> Result<BTreeMap<Vec<u8>, Option<Vec<u8>>>, DispatchError> {
		let host = <T as Config>::IsmpHost::default();
		let state = host
			.state_machine_commitment(proof.height)
			.map_err(|_| Error::<T>::ProofValidationError)?;
		// Select the trie root explicitly instead of letting the relayer-supplied proof choose
		// it. Fee accumulation reads ISMP request/receipt metadata, which lives in the global
		// state trie on EVM chains and in the ISMP child trie (overlay root) on substrate
		// chains.
		let root = if proof.height.id.state_id.is_evm() {
			state.state_root
		} else {
			state.overlay_root.ok_or(Error::<T>::ProofValidationError)?
		};
		let result = state_machine
			.verify_state_proof(&host, keys, root, proof)
			.map_err(|_| Error::<T>::ProofValidationError)?;

		Ok(result)
	}
```
