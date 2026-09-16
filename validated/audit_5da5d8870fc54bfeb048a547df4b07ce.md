### Title
Missing bounds validation in `IntentGatewayV2.setParams` on Tron allows unauthorized fee configuration to brick escrow accounting - (File: evm/tron/contracts/apps/IntentGatewayV2.sol)

### Summary
The Tron variant of `IntentGatewayV2.sol` implements `setParams` with **no validation whatsoever** on the incoming `Params` struct, unlike the canonical EVM implementation (`evm/src/apps/intentsv2/IntentsBase.sol`), which enforces bounds via `_validateParams` on both `initialize` and `_updateParams` (governance-driven `UpdateParams`). This mirrors the reported bug class exactly: validation exists on one configuration path but is missing/inconsistent on another, allowing an out-of-bounds fee/param configuration to be applied.

### Finding Description
In the canonical implementation, `IntentsBase._validateParams` is called uniformly from both `initialize` (evm/src/apps/IntentGatewayV2.sol:114-127) and `_updateParams` (evm/src/apps/intentsv2/IntentsBase.sol:611-628), enforcing: [1](#0-0) 

- non-zero contract host/dispatcher
- `surplusShareBps <= 10_000`
- `protocolFeeBps < 10_000`
- valid price oracle

By contrast, the Tron port's `setParams` performs zero checks — it simply flips `_admin` to `address(0)` and overwrites `_params` in full: [2](#0-1) 

`_params.protocolFeeBps` is later used directly to compute `reducedInputs` for escrow accounting in `placeOrder`: [3](#0-2) 

If `protocolFeeBps` is ever set to `>= 10000` (100%) or an unbounded value, downstream arithmetic in `placeOrder`'s reduced-input computation (subtracting a fee ≥ full input amount) will either underflow/revert (denial of service, freezing all future orders) or, depending on how the reduced amount is computed, escrow an incorrect/zero amount while the commitment hash encodes the original amount — breaking the invariant that escrowed value backs the committed order and creating a fund-freezing/mismatch condition for every order routed through this gateway instance.

### Impact Explanation
This is reachable by whoever is authorized to call `setParams` (the same admin/governance path used by every other `IntentGatewayV2` deployment) supplying a single out-of-bounds `Params` value — with no on-chain guardrail preventing it, unlike the sibling EVM contracts. Because `_params` gates every subsequent `placeOrder` on that Tron instance, a bad configuration (even accidental, e.g. copy-pasting a basis-points value as raw percent) permanently misconfigures fee accounting for the deployed intent gateway, causing either a DoS (all orders revert due to arithmetic issues) or fund mismatches between what is escrowed and what the order commitment represents — a Medium/High severity configuration-safety gap consistent with the reported "H" finding's root cause (inconsistent/missing bound validation between the two places that mutate the fee/param configuration).

### Likelihood Explanation
The `setParams` function is the sole configuration path in this contract (there is no separate cross-chain governance `UpdateParams` validation call visible for the Tron deployment as there is in the mainline `IntentGatewayV2`/`IntentsBase` design), so any authorized caller invoking it with malformed values immediately corrupts the live configuration with no compensating check elsewhere in the contract.

### Recommendation
Add the same bounds checks used in `IntentsBase._validateParams` to `setParams` before committing `_params = p;`: reject zero/non-contract `host`/`dispatcher`, `surplusShareBps > 10_000`, `protocolFeeBps >= 10_000`, and non-contract `priceOracle` if set. Align this Tron port with the canonical `IntentGatewayV2`/`IntentsBase` validation logic so both initialization and update paths enforce identical invariants.

### Proof of Concept
1. Contract admin (or whoever controls `_admin` before the one-time reset) calls `setParams` with `protocolFeeBps = 10000` (100%) or higher. [4](#0-3) 
2. `_params.protocolFeeBps` is now stored unchecked.
3. A user calls `placeOrder`, which computes `protocolFeeBps` for the destination and, since it's ≥ 10000, produces a fully-zeroed or reverting `reducedInputs` computation: [5](#0-4) 
4. Every subsequent order either reverts (permanent DoS for the deployed gateway) or escrows an amount inconsistent with the committed order hash, breaking the escrow invariant for all future orders.

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

**File:** evm/tron/contracts/apps/IntentGatewayV2.sol (L301-311)
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

**File:** evm/tron/contracts/apps/IntentGatewayV2.sol (L338-360)
```text
    function placeOrder(Order memory order, bytes32 graffiti) public payable {
        // Validate that order has inputs
        if (order.inputs.length == 0) revert InvalidInput();

        address hostAddr = host();
        // fill out the order preludes
        order.user = bytes32(uint256(uint160(msg.sender)));
        order.source = IDispatcher(hostAddr).host();
        order.nonce = _nonce++;

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
```
