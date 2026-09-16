### Title
Tron `IntentGatewayV2.setParams` accepts unbounded `protocolFeeBps`/`surplusShareBps`, allowing near-100% confiscation of order inputs - (File: evm/tron/contracts/apps/IntentGatewayV2.sol)

### Summary
The Tron-chain deployment of `IntentGatewayV2` implements `setParams` with only an admin-gate check and no validation of the fee fields, unlike the canonical EVM `IntentGatewayV2`/`IntentsBase` implementation which enforces `surplusShareBps <= 10_000`, `protocolFeeBps < 10_000`, and per-destination fee `< 10_000` via `_validateParams`. This mirrors the `epochFee`-has-no-maximum bug class: an unbounded basis-points fee parameter lets an authorized-but-limited-trust caller siphon nearly all user funds instead of a small protocol cut.

### Finding Description
In the main EVM implementation, all parameter updates flow through `_validateParams`, which bounds `surplusShareBps` to at most 10,000 (100%) and `protocolFeeBps` strictly below 10,000, and the same bound is applied to per-destination fee overrides in `_updateParams`: [1](#0-0) [2](#0-1) 

The Tron variant of `IntentGatewayV2` instead exposes a bare `setParams` function that performs no bounds checking whatsoever on `protocolFeeBps` or `surplusShareBps` before writing the struct into storage: [3](#0-2) 

`protocolFeeBps` is later used directly (without any additional bound check) to compute the fee taken out of every order's inputs in `placeOrder`: [4](#0-3) 

Because `protocolFeeBps` is used as `(originalAmount * protocolFeeBps) / 10_000` with no upper bound enforced at the point it is set, a value at or exceeding 10,000 (100%) — or any large percentage below that — will cause the gateway to deduct the vast majority (or the entirety, and beyond `10_000` would even underflow/revert or, if within range like 9999, take 99.99%) of every user's escrowed input as "protocol fee"/dust, leaving users' actual order barely funded or unfundable.

### Impact Explanation
Any set of parameters written via `setParams` becomes the fee applied to every subsequent `placeOrder` call on the Tron gateway. An unbounded `protocolFeeBps` directly translates into near-total (or total) loss of user deposited funds routed through this Tron `IntentGatewayV2` instance — a concrete theft/fund-freezing outcome for every order placed against it, matching the severity class of the referenced `epochFee` report (a governance/administrative fee parameter capable of draining almost all user value from a bridge/vault flow with no protocol-level ceiling).

### Likelihood Explanation
This requires the ability to call `setParams`, which is restricted to `_admin` (`msg.sender != _admin` reverts). This is a lower bar than a full permissionless bug, but it is still a broken invariant relative to the rest of the codebase: every other deployment path for this exact same parameter set (EVM `IntentGatewayV2`, cross-chain governance `_updateParams`) enforces the `<10_000` bound, and this Tron file is the sole outlier lacking it, so a single misconfiguration, compromised admin key, or overlooked deployment script value (which is passed as raw environment-derived integers, e.g. `PROTOCOL_FEE_BPS`) can silently misconfigure the fee with no on-chain safeguard to catch it.

### Recommendation
Route the Tron `setParams` function through the same `_validateParams` (or an equivalent explicit check) used by the canonical `IntentsBase.sol`, enforcing `p.surplusShareBps <= 10_000` and `p.protocolFeeBps < 10_000` before accepting the new parameters, and apply the identical `< 10_000` bound to any destination-specific fee overrides processed by this contract's `onAccept`/`UpdateParams` handling.

### Proof of Concept
1. Deploy the Tron `IntentGatewayV2` and become `_admin`.
2. Call `setParams(Params({..., protocolFeeBps: 9999, surplusShareBps: 10000, ...}))` — this succeeds with no revert because `setParams` performs no validation: [5](#0-4) 
3. A user calls `placeOrder` depositing e.g. 1000 USDT as `order.inputs[0].amount`.
4. In `placeOrder`, `protocolFee = (1000e6 * 9999) / 10_000 ≈ 999.9 USDT` is deducted as "protocol fee"/dust, leaving the user's escrowed/reduced input at ~0.1 USDT: [6](#0-5) 
5. Essentially the entire deposited amount is unrecoverable by the user/solver, demonstrating the unbounded-fee fund-loss vector.

### Citations

**File:** evm/src/apps/intentsv2/IntentsBase.sol (L592-598)
```text
    function _validateParams(Params memory p) internal view {
        if (p.host == address(0) || p.host.code.length == 0) revert InvalidInput();
        if (p.dispatcher == address(0) || p.dispatcher.code.length == 0) revert InvalidInput();
        if (p.surplusShareBps > 10_000) revert InvalidInput();
        if (p.protocolFeeBps >= 10_000) revert InvalidInput();
        if (p.priceOracle != address(0) && p.priceOracle.code.length == 0) revert InvalidInput();
    }
```

**File:** evm/src/apps/intentsv2/IntentsBase.sol (L611-628)
```text
    function _updateParams(ParamsUpdate memory update) internal {
        _validateParams(update.params);

        emit ParamsUpdated({previous: _params, current: update.params});
        _params = update.params;

        for (uint256 i; i < update.destinationFees.length;) {
            bytes memory chain = update.destinationFees[i].chain;
            uint256 feeBps = update.destinationFees[i].destinationFeeBps;
            if (feeBps >= 10_000) revert InvalidInput();
            _destinationProtocolFees[keccak256(chain)] = feeBps;

            unchecked {
                ++i;
            }
            emit DestinationProtocolFeeUpdated(string(chain), feeBps);
        }
    }
```

**File:** evm/tron/contracts/apps/IntentGatewayV2.sol (L302-311)
```text
    /**
     * @notice Sets the parameters for the IntentGateway.
     * @param p The parameters to be set, encapsulated in a Params struct.
     */
    function setParams(Params memory p) public {
        if (msg.sender != _admin) revert Unauthorized();

        _admin = address(0);
        _params = p;
    }
```

**File:** evm/tron/contracts/apps/IntentGatewayV2.sol (L348-373)
```text
        // Calculate reduced inputs (after protocol fees) for commitment and escrow
        uint256 inputsLen = order.inputs.length;
        // Use destination-specific protocol fee, fallback to source chain fee if zero
        bytes32 destinationHash = keccak256(order.destination);
        uint256 protocolFeeBps = _destinationProtocolFees[destinationHash];
        if (protocolFeeBps == 0) {
            protocolFeeBps = _params.protocolFeeBps;
        }
        TokenInfo[] memory reducedInputs;
        bytes32 commitment;

        if (protocolFeeBps > 0) {
            reducedInputs = new TokenInfo[](inputsLen);
            for (uint256 i; i < inputsLen;) {
                uint256 originalAmount = order.inputs[i].amount;
                uint256 protocolFee = (originalAmount * protocolFeeBps) / 10_000;
                uint256 reducedAmount = originalAmount - protocolFee;
                address token = address(uint160(uint256(order.inputs[i].token)));

                // Emit DustCollected for protocol fee if non-zero
                if (protocolFee > 0) emit DustCollected(token, protocolFee);

                reducedInputs[i] = TokenInfo({token: order.inputs[i].token, amount: reducedAmount});
                unchecked {
                    ++i;
                }
```
