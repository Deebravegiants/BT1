## Confirmed Analog

### Title
`placeOrder` deduplicates output tokens by raw `bytes32` while `_fillSameChain` uses the truncated `address` — non-canonical `token` encodings bypass the duplicate-output-token invariant - (File: `evm/src/apps/IntentGatewayV2.sol`, `evm/src/apps/intentsv2/IntrinsicIntents.sol`)

### Summary
This mirrors the RuniverseLand bug class: a value that encodes a "real" identifier in only part of its bits (the tokenId's leading byte encoding `plotSize`; here, a `bytes32 token` field whose only semantically meaningful part is the lower 160 bits, which get truncated to an `address`) is checked for a safety invariant using the *raw, unreduced* value instead of the *canonicalized* value that downstream logic actually operates on. This lets an unprivileged caller (the order placer) craft two distinct `bytes32` values that collide to the same ERC20 address after truncation, bypassing the "no duplicate output tokens" check that `_fillSameChain`'s partial-fill accounting depends on.

### Finding Description
In `placeOrder`, the duplicate-output-token guard operates on the full, unmodified `bytes32` output token value: [1](#0-0) 

But everywhere else the token is actually used — transfers, escrow accounting, comparisons — the code truncates it to an `address` via `address(uint160(uint256(token)))`, e.g. in `_fillSameChain`: [2](#0-1) 

A user can therefore submit two output entries whose `bytes32` token fields differ only in the unused upper 96 bits (e.g. `bytes32(uint256(uint160(DAI)))` and `bytes32(uint256(uint160(DAI)) | (uint256(1) << 160))`) — both are semantically the same ERC20 (`DAI`) after truncation, but the transient-storage `tload`/`tstore` guard treats them as distinct keys and lets `placeOrder` succeed. This is exactly analogous to `RuniverseLandMinter._mintTokensUsingTokenId` accepting a `tokenId`/`plotSize` pair without checking that the `plotSize`-encoding bits of `tokenId` actually match the `plotSize` argument — the validation is performed on the wrong "view" of the value.

The repo's own regression test comment documents the exact failure mode this check exists to prevent: "same-chain partial fills prematurely finalize repeated output legs" — i.e., `_partialFills[commitment][outputToken]` is keyed by the raw `bytes32` too (see `_fillSameChain` line 73), so a solver filling one of the two colliding-but-distinct output entries does not decrement the "remaining" amount tracked for the other entry, even though both entries physically pay out the same ERC20 token to the beneficiary. [3](#0-2) 

### Impact Explanation
With the duplicate check bypassed via non-canonical `bytes32` encodings:
- `isFullyFilled` and per-leg `_partialFills` bookkeeping become desynchronized from actual token flows, since two "different" output legs are tracked independently in `_partialFills[commitment][outputToken]` keyed by the raw (non-canonical) `bytes32`, even though they pay the identical underlying ERC20 address.
- A solver can potentially satisfy both "distinct" output legs by paying the beneficiary once (or manipulate `remaining`/`amountFilled` state per leg) while `escrowedInputs[i]` is computed independently per index using `order.inputs[i].amount * fillAmount / totalRequired`, allowing proportional escrow release calculations to diverge from what was truly paid out — the regression test this guard was added for explicitly frames this as "premature finalization" of repeated legs, which corresponds to escrow (user funds) being released to a solver disproportionate to the value actually delivered to the beneficiary. This is a concrete theft/fund-accounting-corruption vector reachable by any unprivileged order placer plus a colluding or opportunistic solver — no admin/governance role is required, satisfying the "reachable by unprivileged dispatcher" requirement.

### Likelihood Explanation
Any user can call `placeOrder` directly with a crafted `Order` struct; encoding a `bytes32` with non-zero high bits above an address is trivial and requires no special permissions, gas cost, or timing — a single transaction from a normal wallet. The condition is fully within an ordinary user's control.

### Recommendation
Normalize (mask to `address`) the `token` field before using it as the duplicate-check key in `placeOrder`, i.e. `address token = address(uint160(uint256(order.output.assets[i].token)));` and use `token` (not the raw `bytes32`) as the `tload`/`tstore` key. Equivalently, reject any `TokenInfo.token` whose bits above 160 are non-zero at order-validation time, consistent with how `RuniverseLandMinter` was fixed by removing the ability to submit an unchecked, dual-encoded identifier.

### Proof of Concept
1. Attacker (order placer) submits `placeOrder` with `order.output.assets = [ {token: bytes32(uint256(uint160(DAI))), amount: X}, {token: bytes32(uint256(uint160(DAI)) | (uint256(1) << 200)), amount: Y} ]`.
2. The duplicate-output check in `placeOrder` (lines 197–211) computes `tload`/`tstore` on the two distinct raw `bytes32` values — no collision detected, `placeOrder` succeeds despite both legs resolving to the same DAI ERC20 address.
3. On fill, `_fillSameChain` truncates both entries to the same `address(DAI)` (line 69) but tracks `_partialFills[commitment][outputToken]` keyed by the original distinct `bytes32` values (line 73), and computes `escrowedInputs[i]` independently per index (lines 111–117) — a solver can exploit the resulting mismatch between per-leg accounting and actual DAI transferred to release escrow disproportionate to value delivered, reproducing the same "prematurely finalize repeated output legs" bug the project's own test (`testRevert_PlaceOrder_DuplicateOutputTokens`) was written to prevent, but through a non-canonical encoding that slips past the raw-`bytes32` check.

### Citations

**File:** evm/src/apps/IntentGatewayV2.sol (L197-211)
```text
        // Reject duplicate output tokens
        uint256 outputsLen_ = order.output.assets.length;
        for (uint256 i; i < outputsLen_;) {
            bytes32 token = order.output.assets[i].token;
            assembly ("memory-safe") {
                if tload(token) {
                    mstore(0, 0xb4fa3fb3) // InvalidInput.selector
                    revert(0x1c, 0x04)
                }
                tstore(token, 1)
            }
            unchecked {
                ++i;
            }
        }
```

**File:** evm/src/apps/intentsv2/IntrinsicIntents.sol (L65-70)
```text
        for (uint256 i; i < outputsLen; i++) {
            bytes32 outputToken = order.output.assets[i].token;
            if (options.outputs[i].token != outputToken) revert InvalidInput();

            address token = address(uint160(uint256(outputToken)));
            uint256 totalRequired = order.output.assets[i].amount;
```

**File:** evm/tests/foundry/IntentGatewayV2SameChainTest.sol (L2238-2248)
```text
    /// @notice Placing an order with duplicate output tokens must revert.
    /// Regression test for: same-chain partial fills prematurely finalize repeated output legs.
    function testRevert_PlaceOrder_DuplicateOutputTokens() public {
        TokenInfo[] memory inputs = new TokenInfo[](2);
        inputs[0] = TokenInfo({token: bytes32(uint256(uint160(address(usdc)))), amount: 1000 * 1e6});
        inputs[1] = TokenInfo({token: bytes32(uint256(uint160(address(dai)))), amount: 500 * 1e18});

        // Two output legs both requesting DAI — shares one _partialFills bucket
        TokenInfo[] memory outputAssets = new TokenInfo[](2);
        outputAssets[0] = TokenInfo({token: bytes32(uint256(uint160(address(dai)))), amount: 400 * 1e18});
        outputAssets[1] = TokenInfo({token: bytes32(uint256(uint160(address(dai)))), amount: 600 * 1e18});
```
