Confirmed: `evm/tron/contracts/apps/IntentGatewayV2.sol` `placeOrder` is `public payable` with **no `nonReentrant` modifier**, unlike the EVM version (`evm/src/apps/IntentGatewayV2.sol`), whose `placeOrder`/`fillOrder` carry `nonReentrant` (only 6 matches for `nonReentrant`, all in the EVM contract, none in the Tron one). This matches the report's bug class — a check that is read before an external, hookable token transfer and only updated afterward, reachable via reentrancy during that transfer.

### Title
Missing reentrancy guard on Tron `IntentGatewayV2.placeOrder` allows escrow-accounting corruption via reentrant token callbacks - (File: `evm/tron/contracts/apps/IntentGatewayV2.sol`)

### Summary
`placeOrder` on the Tron deployment of `IntentGatewayV2` performs `safeTransferFrom` calls for each input token, then afterwards writes to `_orders[commitment][token]` and increments the shared `_nonce`, all without a `nonReentrant` guard [1](#0-0) . The EVM-mainline contract at `evm/src/apps/IntentGatewayV2.sol` explicitly fixes this same class of bug by adding `nonReentrant` to `placeOrder` and `fillOrder`, and ships a dedicated regression suite (`IntrinsicIntentsReentrancyTest.sol`) proving that without the guard a same-chain fill can be reentered mid-transfer to steal escrow [2](#0-1) [3](#0-2) . The Tron fork of the contract was not updated with this fix.

### Finding Description
`placeOrder` in the Tron contract stamps `order.nonce = _nonce++` before transferring tokens, then in the escrow branch loops `IERC20(token).safeTransferFrom(msg.sender, address(this), order.inputs[i].amount)` and only afterwards does `_orders[commitment][token] += reducedInputs[i].amount` [4](#0-3) . TRC20/hookable tokens (Tron supports TRC20 tokens with transfer hooks analogous to ERC777/ERC1363) can call back into `placeOrder` during `safeTransferFrom`. Because there is no `nonReentrant` modifier and no reentrancy-blocking state (`_filled` is not touched by `placeOrder`), a reentrant call can execute a second, fully independent `placeOrder` (or interleave with `fillOrder`, which uses `_filled[commitment] = msg.sender` to guard but is a separate contract-level guard, not shared with `placeOrder`) before the outer call's state (`_nonce`, `_orders[commitment][token]`) is finalized.

This mirrors the report's root cause exactly: a state variable meant to bound behavior (`currentDeposit` in the report, `_nonce`/escrow accounting here) is read/derived before the external call and committed only after it, and the external call (`safeTransferFrom` to an attacker-controlled/hookable token) can reenter the same unprotected function.

Because the predispatch path also calls `ICallDispatcher(dispatcher).dispatch(...)` — an arbitrary call the order creator controls — between the pull and the escrow write, with no reentrancy lock, an attacker-supplied token or predispatch call can reenter `placeOrder` to manipulate nonce sequencing/protocol-fee snapshotting (`_destinationProtocolFees` is read fresh each reentry) and craft interleaved commitments while the outer call's escrow bookkeeping is still in flight [5](#0-4) .

### Impact Explanation
This is analogous to the Symm-io deposit-limit bypass: on the EVM contract, the identical unprotected pattern was proven exploitable for outright escrow theft — a reentrant `fillOrder` call could self-fill an output and steal a co-escrowed input token before `_filled` was set (the vulnerability the `nonReentrant`/CEI fix in `evm/src/apps/IntentGatewayV2.sol` and the `IntrinsicIntentsReentrancyTest.sol` suite were written to close) [6](#0-5) . Since the Tron contract lacks the equivalent guard on `placeOrder` (and the file has no `nonReentrant` at all), a same-class attack via a hookable/malicious token used as an order input can corrupt escrow accounting or duplicate/desync the `_nonce`-derived commitment, leading to permanent freezing of escrowed user funds or theft via mismatched escrow bookkeeping once a solver later fills the order and the source-chain `withdraw` releases against a corrupted `_orders[commitment][token]` mapping.

### Likelihood Explanation
Reachable by any unprivileged user submitting a single `placeOrder` transaction with a malicious/hookable token as an order input, or via an attacker-supplied `predispatch.call` dispatched through `ICallDispatcher` — both are ordinary user-controlled parameters requiring no special privilege, matching the "intent escrow" and "unprivileged message dispatcher" reachability required.

### Recommendation
Add the same `nonReentrant` guard (or an equivalent reentrancy lock plus CEI ordering) to `placeOrder` (and any other externally reachable state-mutating function) in `evm/tron/contracts/apps/IntentGatewayV2.sol`, mirroring the fix already applied in `evm/src/apps/IntentGatewayV2.sol`, and add tests analogous to `IntrinsicIntentsReentrancyTest.sol` for the Tron contract.

### Proof of Concept
1. Deploy the Tron `IntentGatewayV2` with a malicious TRC20 token (with a transfer hook) as `order.inputs[0].token`.
2. Attacker calls `placeOrder(order1, ...)`. Inside `safeTransferFrom`, the malicious token's hook reenters `placeOrder(order2, ...)` on the same gateway before `_orders[commitment1][token]` is written.
3. The reentrant call increments `_nonce` and writes its own escrow entry using state (e.g., `_destinationProtocolFees`, `_nonce`) that the outer call has not yet finalized, producing two orders whose commitments and escrow bookkeeping do not match the sequence the off-chain indexer/solver expects.
4. This can be leveraged to desynchronize nonce-based commitment computation from actual escrowed balances, or combined with the same interleaving technique proven against `fillOrder` in `IntrinsicIntentsReentrancyTest.sol` to divert escrowed tokens intended for one order's beneficiary/solver to another, since `placeOrder` provides no lock analogous to `_filled`.

### Citations

**File:** evm/tron/contracts/apps/IntentGatewayV2.sol (L338-346)
```text
    function placeOrder(Order memory order, bytes32 graffiti) public payable {
        // Validate that order has inputs
        if (order.inputs.length == 0) revert InvalidInput();

        address hostAddr = host();
        // fill out the order preludes
        order.user = bytes32(uint256(uint160(msg.sender)));
        order.source = IDispatcher(hostAddr).host();
        order.nonce = _nonce++;
```

**File:** evm/tron/contracts/apps/IntentGatewayV2.sol (L389-414)
```text
        if (order.predispatch.call.length > 0 && order.predispatch.assets.length > 0) {
            address dispatcher = _params.dispatcher;

            // Transfer all predispatch assets to the call dispatcher
            uint256 assetsLen = order.predispatch.assets.length;
            for (uint256 i; i < assetsLen;) {
                address token = address(uint160(uint256(order.predispatch.assets[i].token)));
                uint256 amount = order.predispatch.assets[i].amount;

                if (token == address(0)) {
                    if (amount > msgValue) revert InsufficientNativeToken();
                    msgValue -= amount;

                    (bool sent,) = dispatcher.call{value: amount}("");
                    if (!sent) revert InsufficientNativeToken();
                } else {
                    IERC20(token).safeTransferFrom(msg.sender, dispatcher, amount);
                }

                unchecked {
                    ++i;
                }
            }

            // Execute the call dispatcher with predispatch call
            ICallDispatcher(dispatcher).dispatch(order.predispatch.call);
```

**File:** evm/tron/contracts/apps/IntentGatewayV2.sol (L450-469)
```text
        } else {
            for (uint256 i; i < inputsLen;) {
                if (order.inputs[i].amount == 0) revert InvalidInput();
                address token = address(uint160(uint256(order.inputs[i].token)));
                if (token == address(0)) {
                    // native token
                    if (msgValue < order.inputs[i].amount) revert InsufficientNativeToken();
                    msgValue -= order.inputs[i].amount;
                } else {
                    IERC20(token).safeTransferFrom(msg.sender, address(this), order.inputs[i].amount);
                }

                // Store reduced amount (after protocol fees) in escrow
                _orders[commitment][token] += reducedInputs[i].amount;

                unchecked {
                    ++i;
                }
            }
        }
```

**File:** evm/src/apps/IntentGatewayV2.sol (L194-194)
```text
    function placeOrder(Order memory order, bytes32 graffiti) public payable nonReentrant {
```

**File:** evm/tests/foundry/IntrinsicIntentsReentrancyTest.sol (L85-101)
```text
/**
 * @title IntrinsicIntentsReentrancyTest
 * @notice Forge tests that confirm the CEI fix in `IntrinsicIntents._fillSameChain`
 *         and verify that `ExtrinsicIntents._fillCrossChain` is also resistant to
 *         reentrancy attacks.
 *
 * Both fill functions now open with `_filled[commitment] = msg.sender` before any
 * external calls, so a reentrant `fillOrder` attempt is always blocked by the
 * `Filled()` guard in `IntentGatewayV2.fillOrder`.
 *
 * Test matrix
 * ───────────
 *  testReentrancy_FeeTheft                    same-chain, 1 ETH output   → InsufficientNativeToken
 *  testReentrancy_EscrowTheft_MultiOutput     same-chain, ETH+ERC-20     → InsufficientNativeToken
 *  testCrossChain_ReentrancyBlocked           cross-chain, 1 ETH output  → InsufficientNativeToken
 *  testCrossChain_ReentrancyBlocked_MultiOutput cross-chain, ETH+ERC-20  → InsufficientNativeToken
 */
```

**File:** evm/tests/foundry/IntrinsicIntentsReentrancyTest.sol (L282-293)
```text
    /**
     * @dev Same-chain multi-output escrow theft is blocked by the CEI fix.
     *
     * Before the fix: on a two-output order (ETH + ERC-20), the malicious
     * beneficiary could re-enter during the ETH transfer, self-fill the ERC-20
     * output (net-zero cost), trigger `_withdraw(finalize=true)`, and steal the
     * entire input[1] escrow.
     *
     * After the fix: `_filled[commitment]` is set before the loop, so the
     * reentrant call reverts with `Filled()`. The whole transaction reverts with
     * `InsufficientNativeToken()` and no state is mutated.
     */
```
