### Title
Missing bounds validation on `UpdateParams` in Tron `IntentGatewayV2.onAccept` permanently bricks/drains order placement - (File: `evm/tron/contracts/apps/IntentGatewayV2.sol`)

### Summary
The Tron variant of `IntentGatewayV2.onAccept` applies a governance-originated `ParamsUpdate` (`_params = update.params;` and `_destinationProtocolFees[stateMachineId] = feeBps;`) without any range validation on `protocolFeeBps` / `destinationFeeBps`. The mainline EVM contract (`IntentsBase.sol`) enforces `protocolFeeBps < 10_000` and `destinationFeeBps < 10_000` (i.e. strictly less than 100%) via `_validateParams`/`_updateParams` before committing the same fields, but this Tron contract's `onAccept` handler for `RequestKind.UpdateParams` skips that check entirely.

### Finding Description
In `evm/tron/contracts/apps/IntentGatewayV2.sol`, `onAccept` handles `RequestKind.UpdateParams` like this: [1](#0-0) 

It decodes the `ParamsUpdate` and directly overwrites `_params` and `_destinationProtocolFees[stateMachineId]` with attacker/governance-supplied `feeBps` values with **no upper-bound check**.

Compare to the canonical EVM implementation, `IntentsBase._validateParams`/`_updateParams`, which explicitly rejects `protocolFeeBps >= 10_000` and any `destinationFeeBps >= 10_000` before applying an update: [2](#0-1) 

The unchecked `protocolFeeBps`/`destinationFeeBps` is then consumed unguarded in `placeOrder`, where it directly reduces the escrowed input: [3](#0-2) 

`protocolFee = (originalAmount * protocolFeeBps) / 10_000` and `reducedAmount = originalAmount - protocolFee` performs unchecked (Solidity 0.8 checked) arithmetic. If `protocolFeeBps >= 10_000` (≥100%), `protocolFee >= originalAmount`, so `reducedAmount` underflows and every `placeOrder` call for that destination permanently reverts — a config error is a one-way irreversible bricking of the route (repaired only by another correct `UpdateParams` message, which itself is not validated on-chain either). If `protocolFeeBps` is set to exactly `10_000` (100%), `placeOrder` does not revert but escrows `reducedAmount = 0` for every user input, silently confiscating 100% of every subsequent depositor's funds as protocol "dust" while the user receives nothing escrowed for the filler to act on — a direct, ongoing loss of user funds with no code-level protection against it.

This is the same root-cause class as the reference report (`Game.setNegativeRewardFactor` missing a `< 100%` bound): a percentage/basis-point parameter that governs how much of a user's deposit is retained by the protocol is applied without a sanity check that would prevent it exceeding 100%, even though the exact same codebase enforces that bound in its sibling (mainline EVM) implementation, confirming the intended invariant.

### Impact Explanation
- Freezing of funds: setting `protocolFeeBps`/`destinationFeeBps` ≥ 10,000 on the Tron gateway causes an unconditional underflow revert in `placeOrder`, permanently freezing the `placeOrder` entry point for that destination (or globally, for `protocolFeeBps`) until another governance message corrects it — this qualifies as "a route unable to deliver messages."
- Theft/loss of funds: setting the value to exactly 10,000 (100%) does not revert, but every subsequent order taker's entire input is siphoned into protocol dust (`reducedAmount = 0`), causing concrete, irreversible loss of user deposited funds with no economic benefit to the filler/solver flow, and no on-chain safeguard preventing it.
- Because this path is reached purely by relaying a legitimately-sourced hyperbridge `UpdateParams` message (the `onAccept` source check only verifies the message came from `hyperbridge`, not that its *content* is sane), a single fat-fingered or malformed governance payload — encoded and dispatched exactly like the parallel, already-validated EVM path — silently bricks or drains the Tron deployment, whereas the identical operation on the audited/mainline EVM contracts is defended by `_validateParams`.

### Likelihood Explanation
Medium: this requires a governance-originated `UpdateParams` message to be dispatched with an out-of-range `protocolFeeBps`/`destinationFeeBps` value. Given the mainline EVM contract enforces this exact invariant on the same message type, it is evident this is an unintentional omission in the Tron port rather than an intentional design choice, making an operational mistake (which the mainline code already treats as foreseeable/needing defense) plausible. Any relayer can deliver a genuine hyperbridge-originated `UpdateParams` request; the vulnerability is that the destination contract fails to defend itself against out-of-range values that the source pallet may not itself bound (the intents-coprocessor Rust `ParamsUpdate::update` in `types.rs` was not confirmed to enforce a bps ceiling either, so the validation gap is not clearly closed upstream).

### Recommendation
Add the same bound check present in `IntentsBase._validateParams` to the Tron `onAccept` `UpdateParams` branch: reject (or clamp) `update.params.protocolFeeBps >= 10_000` and any `update.destinationFees[i].destinationFeeBps >= 10_000` before writing `_params`/`_destinationProtocolFees`. Apply the identical validation to `setParams` in the same file, which currently sets `_params = p` with zero validation at all.

### Proof of Concept
1. Hyperbridge governance (or a compromised/misconfigured relay of a legitimate governance message) dispatches a `RequestKind.UpdateParams` `PostRequest` to the Tron `IntentGatewayV2` with `update.params.protocolFeeBps = 10_000` (or higher).
2. `onAccept` verifies only `request.source == hyperbridge` and then executes `_params = update.params;` unconditionally: [4](#0-3) 
3. Any user subsequently calls `placeOrder` with a nonzero `order.inputs[i].amount`.
4. In the fee-reduction loop, `protocolFee = (originalAmount * 10_000) / 10_000 = originalAmount`, so `reducedAmount = originalAmount - protocolFee = 0`: [5](#0-4) 
   The user's full token amount is pulled via `safeTransferFrom` into the gateway, but `_orders[commitment][token]` is credited with `0`, so the order can never be legitimately filled/redeemed for that amount — the user's funds are stuck as unclaimable dust.
5. If `protocolFeeBps > 10_000` instead, step 4's subtraction underflows and reverts, permanently DoS'ing `placeOrder` for every user until governance sends a corrected update.

### Citations

**File:** evm/tron/contracts/apps/IntentGatewayV2.sol (L359-374)
```text
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
            }
```

**File:** evm/tron/contracts/apps/IntentGatewayV2.sol (L637-660)
```text
        // only hyperbridge is permitted to perfom these actions
        if (keccak256(incoming.request.source) != keccak256(IDispatcher(host()).hyperbridge())) revert Unauthorized();
        if (kind == RequestKind.NewDeployment) {
            NewDeployment memory body = abi.decode(incoming.request.body[1:], (NewDeployment));
            _instances[keccak256(body.stateMachineId)] = body.gateway;

            emit NewDeploymentAdded({stateMachineId: body.stateMachineId, gateway: body.gateway});
        } else if (kind == RequestKind.UpdateParams) {
            // Decode the body which includes optional destination-specific protocol fee updates
            ParamsUpdate memory update = abi.decode(incoming.request.body[1:], (ParamsUpdate));
            emit ParamsUpdated({previous: _params, current: update.params});
            _params = update.params;

            // Update destination-specific protocol fees if provided
            for (uint256 i; i < update.destinationFees.length;) {
                bytes32 stateMachineId = update.destinationFees[i].stateMachineId;
                uint256 feeBps = update.destinationFees[i].destinationFeeBps;
                _destinationProtocolFees[stateMachineId] = feeBps;

                unchecked {
                    ++i;
                }
                emit DestinationProtocolFeeUpdated(stateMachineId, feeBps);
            }
```

**File:** evm/src/apps/intentsv2/IntentsBase.sol (L592-628)
```text
    function _validateParams(Params memory p) internal view {
        if (p.host == address(0) || p.host.code.length == 0) revert InvalidInput();
        if (p.dispatcher == address(0) || p.dispatcher.code.length == 0) revert InvalidInput();
        if (p.surplusShareBps > 10_000) revert InvalidInput();
        if (p.protocolFeeBps >= 10_000) revert InvalidInput();
        if (p.priceOracle != address(0) && p.priceOracle.code.length == 0) revert InvalidInput();
    }

    /**
     * @dev Updates the gateway's configuration parameters and per-destination protocol fees.
     * Called by Hyperbridge governance to modify fee settings, host address, dispatcher,
     * price oracle, and other operational parameters.
     *
     * Validates all params before applying. Emits ParamsUpdated with the old and new params,
     * then iterates over any destination-specific fee overrides and applies them to
     * `_destinationProtocolFees`.
     *
     * @param update The parameter update containing new params and destination fee overrides.
     */
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
