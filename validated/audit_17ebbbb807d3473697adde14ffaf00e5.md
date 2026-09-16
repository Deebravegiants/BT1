This confirms the analog: the Intent Gateway places no restriction whatsoever on which ERC20 token addresses may appear in `order.inputs`, and `_withdraw` / `withdraw` iterate over **all** the order's tokens in a single loop, using `safeTransfer`/`.call` that reverts (or the caller's `require(success)` on Tron variant) the entire withdrawal on a single failing token — exactly the class of bug KingNFT reported against OpenQ's `fundBountyToken`/`claimBalance` pattern. [1](#0-0) [2](#0-1) [3](#0-2) 

### Title
Attacker-chosen malicious ERC20 in `order.inputs` permanently freezes escrow via revert-on-transfer loop in `_withdraw`/`withdraw` - (File: evm/src/apps/intentsv2/IntentsBase.sol, evm/tron/contracts/apps/IntentGatewayV2.sol)

### Summary
`placeOrder` accepts arbitrary ERC20 token addresses for `order.inputs` with no whitelist or allow-list check [4](#0-3) . `_withdraw` (EVM mainline) and `withdraw` (Tron variant) release escrow by iterating over *all* of an order's tokens in a single loop and transferring each one with `safeTransfer`/low-level `.call` whose failure reverts the whole function [1](#0-0) [5](#0-4) . This is the exact pattern flagged in the OpenQ report: a single attacker-supplied non-whitelisted/blacklist-capable token embedded in a multi-token operation can force every settlement of that operation to permanently revert, freezing the legitimate tokens escrowed alongside it.

### Finding Description
When a user places a same-chain or cross-chain order, they choose the set of `order.inputs` tokens themselves; the contract only rejects duplicate token addresses, it never validates that a token is a "normal" transferable ERC20 [6](#0-5) . An attacker can therefore construct an order with two inputs: a legitimate token (e.g. USDC) and a custom ERC20 with an owner-controlled blacklist/pausable transfer function that always reverts for a chosen address.

Both settlement paths funnel through the shared withdrawal routine:
- Same-chain fill/cancel and cross-chain settlement (`RedeemEscrow`/`RefundEscrow`) call `_withdraw`/`withdraw`, which loops `for (uint256 i; i < len; i++)` over `body.tokens` and calls `IERC20(token).safeTransfer(beneficiary, amount)` (mainline) or a raw `.call` with a `require(success)`-equivalent revert (Tron) [7](#0-6) [8](#0-7) .
- Because the loop is atomic and unconditional, if the malicious token's `transfer` reverts for the current `beneficiary` (the solver on a fill, or the user on a cancel/refund), the *entire* transaction reverts — including the transfer of the legitimate co-escrowed token.
- Critically, `_filled[commitment]`/`_orders[commitment][token]` are only mutated as part of the same reverting call, so the order permanently remains claimable-but-unclaimable: every subsequent attempt to fill, cancel, or settle it hits the same poisoned token and reverts identically. There is no per-token withdrawal or skip-and-continue mechanism to salvage the good token.

This mirrors the OpenQ finding precisely: `claimBalance()`/`claimTiered()` was called in a loop over all funded token addresses by `ClaimManagerV1`, and a single malicious blacklisted token blocked the entire `claimBounty()` — here, a single malicious token in `order.inputs` blocks the entire settlement/withdrawal of an order.

### Impact Explanation
This freezes the *other legitimate escrowed tokens* in the same order permanently, since there is no code path to withdraw a subset of tokens or to skip a failing transfer. For cross-chain orders, this also poisons the destination `RedeemEscrow`/source `RefundEscrow` message forever — a relayer can resubmit indefinitely and it will always revert, meaning the message can never be delivered/settled, which additionally falls into "a route unable to deliver messages" for that specific commitment. Depending on order construction (e.g., attacker deposits a large amount of a real, valuable token alongside the poison token as one of several inputs), a solver who has already delivered real output value to the beneficiary can be permanently denied their promised escrow, and the user's own remaining escrow on cancel/refund is likewise permanently locked. This is a concrete permanent freezing of funds.

### Likelihood Explanation
Likelihood is high: `placeOrder` is a fully public, unprivileged entry point reachable by any submitted transaction, requires no special permissions, and the only cost to the attacker is deploying a trivial ERC20 with a blacklist/pausable transfer hook and funding a minimal amount of the poison token as one of the order's inputs. No governance or admin action is required to trigger the freeze — only a legitimate solver or the attacker themself triggering `fillOrder`/`cancelOrder` against the poisoned order.

### Recommendation
Do not perform escrow release for all tokens atomically in one all-or-nothing loop. Options:
1. Make individual token transfers within `_withdraw`/`withdraw` best-effort (e.g., wrap each transfer in a try/catch or low-level call that does not revert the whole function on failure), crediting the beneficiary an internal claimable balance for tokens that fail to transfer, so they can be retried/pulled later without blocking the rest.
2. Alternatively, split escrow release into a per-token claim function so a poisoned token cannot block release of the other tokens in the same order.
3. Consider restricting `order.inputs`/`order.output.assets` token addresses to a governance-curated allow-list, closing the same class of attack that the OpenQ report originally targeted.

### Proof of Concept
1. Attacker deploys `EvilToken`, an ERC20 whose `transfer`/`transferFrom` reverts whenever `to == blacklisted[to]`, and sets `blacklisted[solverAddress] = true` (or targets `order.user` for the cancel path).
2. Attacker calls `placeOrder` with `order.inputs = [ {token: USDC, amount: X}, {token: EvilToken, amount: 1} ]` and a normal output request; escrow for both tokens is credited under the same `commitment` [6](#0-5) .
3. A solver fills the order, delivering the requested output tokens to the beneficiary and triggering the `RedeemEscrow` settlement (same-chain) or cross-chain message that ultimately calls `_withdraw`/`withdraw` with `body.tokens = order.inputs` and `beneficiary = solver`.
4. Inside `_withdraw`, the loop first transfers USDC successfully, then reaches `EvilToken.transfer(solver, 1)`, which reverts because `solver` is blacklisted; `safeTransfer` propagates the revert, rolling back the entire transaction, including the USDC transfer that had already "succeeded" within the same call frame [9](#0-8) .
5. Every subsequent call to settle/withdraw this commitment (retries by relayers, or repeated `fillOrder`/`cancelOrder` attempts) hits the same revert — the USDC (and any other legitimate token) escrowed for this order is permanently unrecoverable, and the solver who already delivered value on the destination chain never receives their input tokens.

### Citations

**File:** evm/src/apps/intentsv2/IntentsBase.sol (L451-470)
```text
    function _withdraw(WithdrawalRequest memory body, bool isRefund, bool finalize) internal {
        address beneficiary = address(uint160(uint256(body.beneficiary)));
        if (finalize) _filled[body.commitment] = beneficiary;

        uint256 len = body.tokens.length;
        for (uint256 i; i < len; i++) {
            address token = address(uint160(uint256(body.tokens[i].token)));
            uint256 amount = body.tokens[i].amount;
            if (amount == 0) continue;

            uint256 escrowed = _orders[body.commitment][token];
            if (escrowed == 0) revert UnknownOrder();

            _orders[body.commitment][token] = escrowed - amount;
            if (token == address(0)) {
                _sendValue(beneficiary, amount);
            } else {
                IERC20(token).safeTransfer(beneficiary, amount);
            }
        }
```

**File:** evm/tron/contracts/apps/IntentGatewayV2.sol (L691-722)
```text
    function withdraw(WithdrawalRequest memory body, bool isRefund) internal {
        address beneficiary = address(uint160(uint256(body.beneficiary)));
        _filled[body.commitment] = beneficiary;

        // redeem escrowed tokens
        uint256 len = body.tokens.length;
        for (uint256 i; i < len;) {
            address token = address(uint160(uint256(body.tokens[i].token)));
            uint256 amount = body.tokens[i].amount;
            if (_orders[body.commitment][token] == 0) revert UnknownOrder();

            if (token == address(0)) {
                (bool sent,) = beneficiary.call{value: amount}("");
                if (!sent) revert InsufficientNativeToken();
            } else {
                (bool success,) = token.call(abi.encodeWithSelector(IERC20.transfer.selector, beneficiary, amount));
                if (!success) revert TransferFailed();
            }

            _orders[body.commitment][token] -= amount;
            unchecked {
                ++i;
            }
        }

        // redeem tx fees
        uint256 fees = _orders[body.commitment][TRANSACTION_FEES];
        if (fees > 0) {
            address feeToken = IDispatcher(host()).feeToken();
            (bool success,) = feeToken.call(abi.encodeWithSelector(IERC20.transfer.selector, beneficiary, fees));
            if (!success) revert TransferFailed();
            delete _orders[body.commitment][TRANSACTION_FEES];
```

**File:** evm/src/apps/IntentGatewayV2.sol (L194-256)
```text
    function placeOrder(Order memory order, bytes32 graffiti) public payable nonReentrant {
        if (order.inputs.length == 0) revert InvalidInput();

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
        // Clean up transient storage so repeated placeOrder calls in the same tx don't false-positive.
        for (uint256 i; i < outputsLen_;) {
            bytes32 token = order.output.assets[i].token;
            assembly ("memory-safe") {
                tstore(token, 0)
            }
            unchecked {
                ++i;
            }
        }

        address hostAddr = host();
        order.user = bytes32(uint256(uint160(msg.sender)));
        order.source = IDispatcher(hostAddr).host();
        order.nonce = _nonce++;

        uint256 inputsLen = order.inputs.length;

        // Phase 1: Transfer tokens and record actual received amounts.
        // For fee-on-transfer tokens, the gateway receives less than the requested amount.
        // We mutate order.inputs to reflect actual received so the commitment and escrow
        // are consistent with what the gateway holds.
        uint256 msgValue = msg.value;
        if (order.predispatch.call.length > 0 && order.predispatch.assets.length > 0) {
            address dispatcher = _params.dispatcher;

            uint256 assetsLen = order.predispatch.assets.length;
            for (uint256 i; i < assetsLen;) {
                address token = address(uint160(uint256(order.predispatch.assets[i].token)));
                uint256 amount = order.predispatch.assets[i].amount;
                if (amount == 0) revert InvalidInput();

                if (token == address(0)) {
                    if (amount > msgValue) revert InsufficientNativeToken();
                    msgValue -= amount;

                    _sendValue(dispatcher, amount);
                } else {
                    IERC20(token).safeTransferFrom(msg.sender, dispatcher, amount);
                }

                unchecked {
                    ++i;
                }
            }
```

**File:** evm/src/apps/IntentGatewayV2.sol (L364-373)
```text
        for (uint256 i; i < inputsLen;) {
            address token = address(uint160(uint256(order.inputs[i].token)));
            // Reject duplicate input tokens
            if (_orders[commitment][token] != 0) revert InvalidInput();
            _orders[commitment][token] = reducedInputs[i].amount;

            unchecked {
                ++i;
            }
        }
```
