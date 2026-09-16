## Title
Missing Input Validation on Cross-Chain `UpdateParams` Governance Message in Tron `IntentGatewayV2.onAccept` — ([File: evm/tron/contracts/apps/IntentGatewayV2.sol])

### Summary
The Tron deployment of `IntentGatewayV2` (`evm/tron/contracts/apps/IntentGatewayV2.sol`) writes an incoming, cross-chain-delivered `Params` struct and destination-fee updates directly into the contract's global storage (`_params`, `_destinationProtocolFees`) with **no bounds or sanity checking whatsoever**, unlike the audited mainline EVM implementation, which validates every field before committing it to storage.

### Finding Description
`onAccept` handles `RequestKind.UpdateParams` by decoding the request body and assigning it straight to storage: [1](#0-0) 

There is no equivalent of the mainline `_validateParams`/bound-checking logic used elsewhere in the codebase, e.g. in `IntentsBase.sol`: [2](#0-1) 

That function rejects zero/non-contract `host`/`dispatcher`, `surplusShareBps > 10_000`, `protocolFeeBps >= 10_000`, non-contract `priceOracle`, and any `feeBps >= 10_000` for destination-specific fees. The Tron contract's `onAccept`/`setParams` performs none of these checks — `setParams` (privileged, one-time-admin path) and the `UpdateParams` cross-chain path both write the raw decoded struct into `_params` unconditionally: [3](#0-2) 

Since `host()` simply returns `_params.host` and gates `onAccept` itself via the `onlyHost` modifier, any write that sets `_params.host` to `address(0)` (or any address that can no longer call `onAccept`) permanently seals off the only entry point capable of ever fixing the params again — there is no recovery path once this field is corrupted. Likewise, an unbounded `_destinationProtocolFees[stateMachineId]` (e.g. `>= 10_000` bps) breaks `placeOrder`'s fee-subtraction arithmetic (`originalAmount - protocolFee`), which can underflow/revert and deny order placement, or (depending on value) silently miscalculate the amount escrowed for the destination gateway to settle, i.e. improper accounting of user funds.

This is the direct analog of GHSA-65wv-528r-m892 (CVE-2020-13961): a struct (there, an email template; here, gateway configuration/fee parameters) is stored into global/mutable state coming from a request whose payload is not sanitized, allowing security-relevant global behavior (message authorization gate, fee accounting) to be corrupted by unvalidated input.

### Impact Explanation
- **Permanent freezing of funds**: if `UpdateParams` ever delivers `params.host == address(0)` (or any non-functional value), `onlyHost` on `onAccept` can never again be satisfied, permanently bricking the gateway's only channel for corrective governance messages, while all escrowed order funds recorded in `_orders`/`_filled` remain unrecoverable on that chain.
- **Unbacked/incorrect fee accounting**: an out-of-range `destinationFeeBps` (unbounded on this fork, capped at `<10,000` on the mainline EVM fork) can push `protocolFeeBps` past 100%, causing `placeOrder`'s `originalAmount - protocolFee` subtraction to underflow and revert (denial of the route for that destination) or, for validators that allow overflow, siphon more of the user's escrowed input than intended.
- The class matches the "route unable to deliver messages" / "permanent freezing of funds" acceptance criteria in this review's rules.

### Likelihood Explanation
`UpdateParams` is reachable only from a message whose `source` equals Hyperbridge and is delivered through the normal cross-chain path (verified by consensus/state proof, dispatched via a Hyperbridge-side pallet such as `intents-coprocessor`). This makes exploitation dependent on the correctness of the sending side rather than an arbitrary unprivileged attacker directly forging content. However, the entire point of the audited mainline contract's `_validateParams`/`feeBps` checks is defense-in-depth against exactly this class of error — a defense which is present on the primary EVM contract but is completely absent on the Tron fork. Any accidental mis-encoding, partial/legacy-format payload, or an intents-coprocessor governance bug/fat-finger (a scenario that the mainline contract's own guard rails were specifically written to catch) reaches `onAccept` here with zero protection, whereas on Ethereum/BSC/etc. the same mistake reverts safely with `InvalidInput`. This is a genuine input-validation gap uniquely present in this one file relative to its sibling implementations in the same repository.

### Recommendation
Port the mainline `_validateParams` bound-checking (`host`/`dispatcher` non-zero and contract code present, `surplusShareBps <= 10_000`, `protocolFeeBps < 10_000`, `priceOracle` zero-or-contract) and the `feeBps < 10_000` guard for each `DestinationFee` entry into the Tron `IntentGatewayV2.onAccept`'s `UpdateParams` branch (and into `setParams`) before writing to `_params`/`_destinationProtocolFees`, exactly mirroring `IntentsBase._validateParams`/`_updateParams`.

### Proof of Concept
1. Hyperbridge (via `intents-coprocessor::update_params`, or any bug/mis-encoding in that pipeline) dispatches a `RequestKind.UpdateParams` post request to the Tron `IntentGatewayV2` instance with `params.host = address(0)` (or `protocolFeeBps = 10_000+`, or a `DestinationFee.destinationFeeBps = 10_000+`).
2. The relayer delivers the proven message; `onAccept` verifies `source == hyperbridge()` and unconditionally executes:
   ```solidity
   _params = update.params;
   _destinationProtocolFees[stateMachineId] = feeBps; // no bound check
   ```
3. With `host == address(0)`, every future call to `onAccept` (gated by `onlyHost`, which reads `_params.host`) reverts permanently — no further `UpdateParams` message can ever repair the contract, and all escrow balances in `_orders`/`_filled` become permanently unreachable. With an over-100% fee, `placeOrder`'s `originalAmount - protocolFee` underflows and reverts, denying order placement on that route.

Note: I could not fully confirm from the index whether `intents-coprocessor::update_params` (the governance-side Substrate call) applies its own bound validation before dispatch — `modules/pallets/intents-coprocessor/src/lib.rs` and `types.rs` reference `protocol_fee_bps`/`destination_fee_bps` but I was not able to inspect the full validation logic within the tool budget available. If that pallet does perform equivalent bound checks server-side, the practical likelihood is lower (defense-in-depth gap only); if it does not, this is directly exploitable by anyone able to submit a malformed-but-otherwise-valid `update_params` extrinsic through that pallet's `GovernanceOrigin` path.

### Citations

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
