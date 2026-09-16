### Title
Tron `IntentGatewayV2.onAccept` (`UpdateParams`) skips protocol-fee/params bounds validation the mainline EVM gateway enforces - ([File: evm/tron/contracts/apps/IntentGatewayV2.sol])

### Summary
The Tron variant of `IntentGatewayV2` applies a cross-chain `UpdateParams` governance message directly, with no equivalent of the mainline `IntentsBase._validateParams`/`_updateParams` bounds checks (`host`/`dispatcher` code checks, `surplusShareBps <= 10_000`, `protocolFeeBps < 10_000`, and per-destination `feeBps < 10_000`). This mirrors the reported Compound `GovernorBravoDelegate`/`Delegator` class of bug: sensitive parameters are accepted and stored without range/sanity checks.

### Finding Description
On the mainline EVM implementation, `IntentsBase._validateParams` enforces invariants before committing new params, and `_updateParams` further checks that per-destination `feeBps < 10_000`: [1](#0-0) 

The Tron port's `onAccept` handles the same `UpdateParams` governance action but writes `_params` and `_destinationProtocolFees` unconditionally, with **no** call to any `_validateParams`-equivalent and **no** upper bound on `feeBps`: [2](#0-1) 

Likewise its one-shot `setParams` initializer has no validation of `p.host`, `p.dispatcher` (code presence), `surplusShareBps`, or `protocolFeeBps`, unlike the mainline gateway's `initialize`, which calls `_validateParams`: [3](#0-2) [4](#0-3) 

Because `_params.protocolFeeBps` (or a per-destination override) is used unchecked in `placeOrder` to compute `reducedAmount = originalAmount - protocolFee`, a `protocolFeeBps`/`feeBps` value at or above `10_000` (100%) causes `protocolFee` to exceed `originalAmount`: [5](#0-4) 

which underflows and unconditionally reverts every `placeOrder` call routed to that destination (or every call, if it's the default `_params.protocolFeeBps`) — permanently freezing all future intent placement to that chain/route until governance issues another corrective update. There is no way for a user to work around this once the bad value lands on-chain, since `placeOrder` is the only entry point that reads it and it always reverts before escrow.

### Impact Explanation
This is a livelock/DoS of the intent-placement route: any account fees value ≥ 10,000 bps that reaches `_params`/`_destinationProtocolFees` (whether through a governance mistake, an implementation bug in `intents-coprocessor` computing `ParamsUpdate`, or a future regression) permanently bricks `placeOrder` for the affected destination, matching the "route unable to deliver messages" acceptance criterion. It is a direct consequence of the missing input validation that the mainline gateway explicitly added (and which this report class calls out), so it is the same class of defect, just unguarded on this target.

### Likelihood Explanation
Medium. The path requires a governance-originated `UpdateParams`/`SweepDust`-style message with a bad `feeBps`/`protocolFeeBps` value to be dispatched (source is checked to be Hyperbridge, so this cannot be forged by an arbitrary relayer), but nothing on this contract prevents that value from being accepted and applied, whereas the mainline EVM contract added exactly this guard as a defense-in-depth measure — the asymmetry itself is the vulnerability: the mainline code treats an out-of-range fee as something that must never be persisted, while the Tron port persists it unconditionally.

### Recommendation
Port `IntentsBase._validateParams`/`_updateParams`'s bounds checks into the Tron `IntentGatewayV2`:
- Add a `_validateParams` helper checking `p.host != address(0) && code.length > 0`, `p.dispatcher != address(0) && code.length > 0`, `surplusShareBps <= 10_000`, `protocolFeeBps < 10_000` and call it from both `setParams` and the `UpdateParams` branch of `onAccept`.
- Enforce `feeBps < 10_000` before writing `_destinationProtocolFees[stateMachineId]` in `onAccept`.

### Proof of Concept
1. Hyperbridge governance dispatches a `RequestKind.UpdateParams` message to the Tron `IntentGatewayV2` with `update.params.protocolFeeBps = 10_000` (or a `destinationFees[i].destinationFeeBps = 10_000`).
2. The registered relayer delivers it; `onAccept` decodes and stores it unconditionally (`evm/tron/contracts/apps/IntentGatewayV2.sol:644-660`) — no revert.
3. Any user subsequently calls `placeOrder` for that destination; `protocolFee = (originalAmount * 10_000) / 10_000 = originalAmount`, so `reducedAmount = originalAmount - protocolFee = 0`... for any bps > 10_000 (e.g., 10_001), `protocolFee > originalAmount` and `originalAmount - protocolFee` underflows in Solidity's checked arithmetic, reverting the transaction.
4. `placeOrder` for that destination is now permanently unusable until another governance message corrects the value, demonstrating the freeze/DoS impact of the missing bound.

### Citations

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

**File:** evm/tron/contracts/apps/IntentGatewayV2.sol (L644-660)
```text
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

**File:** evm/src/apps/IntentGatewayV2.sol (L114-127)
```text
    function initialize(Params memory p, bytes[] memory peerChains, address relayer)
        public
        onlyFresh
        reinitializer(VERSION)
    {
        uint256 peersLength = peerChains.length;
        for (uint256 i = 0; i < peersLength; i++) {
            Deployment memory deployment = Deployment({chain: peerChains[i], gateway: address(this)});
            _addDeployment(deployment);
        }
        _validateParams(p);
        _params = p;
        _setRelayer(relayer);
    }
```
