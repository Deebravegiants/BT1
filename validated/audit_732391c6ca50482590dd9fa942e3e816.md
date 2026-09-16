## Analysis

The reported bug class — failing to check the actual success/return value of an ERC20 transfer (only checking that a low-level `.call()` didn't revert, not that the token's `transfer()` returned `true`) — has a direct analog in Hyperbridge's **Tron IntentGateway** implementation.

### Root Cause

In `evm/tron/contracts/apps/IntentGatewayV2.sol`, the `withdraw()` function (called from `onAccept()` when a `RedeemEscrow`/`RefundEscrow` message is settled, and from `onGetResponse()` on cross-chain cancellation) releases escrowed tokens using a raw low-level call instead of `SafeERC20.safeTransfer`: [1](#0-0) 

Specifically:
```solidity
(bool success,) = token.call(abi.encodeWithSelector(IERC20.transfer.selector, beneficiary, amount));
if (!success) revert TransferFailed();
```
This only verifies that the external call itself did not revert — it never decodes the returned `bool` from `transfer()`. Any ERC20/TRC20 token that implements the classic OpenZeppelin-style interface (returns `false` on failure instead of reverting — e.g., due to a paused/blacklisted transfer, insufficient allowance edge case in a non-standard implementation, or any token quirk) will make `success == true` even though the tokens never moved.

The same unchecked pattern is repeated in the same file for:
- The `SweepDust` handler in `onAccept()`: [2](#0-1) 
- The transaction-fee payout inside `withdraw()`: [3](#0-2) 

Notably, the contract does import and use `SafeERC20` correctly for **inbound** transfers in `placeOrder()` (`IERC20(token).safeTransferFrom(...)` [4](#0-3) ), but deliberately switches to unchecked raw calls for **outbound** escrow release, creating an inconsistency that matches exactly the class of bug the external report flags.

### Impact

Because `withdraw()` unconditionally decrements the escrow accounting (`_orders[body.commitment][token] -= amount;`) and marks the order as filled (`_filled[body.commitment] = beneficiary;`) *before/regardless of* whether the token transfer actually succeeded in substance (only checking call-level revert, not the boolean return value), a silent `transfer()` failure results in:
- The beneficiary/solver never receiving the escrowed tokens.
- The escrow bookkeeping being permanently zeroed out with no retry path, since the order is already marked filled and the ISMP request already consumed (replay-protected).
- The tokens remaining permanently stuck in the `IntentGatewayV2` contract, unbacked by any accounting entry — a permanent freezing of user/solver funds.

This is reachable by any user placing an order and any solver filling/settling it — an ordinary transaction flow — whenever the input/fee token used has non-reverting `transfer()` failure semantics.

### Title
Unchecked ERC20 `transfer()` return value in Tron IntentGatewayV2 escrow release causes permanent loss of escrowed funds - (File: `evm/tron/contracts/apps/IntentGatewayV2.sol`)

### Summary
`withdraw()` (and the `SweepDust` handler) in the Tron variant of `IntentGatewayV2` release escrowed tokens via a raw `token.call(abi.encodeWithSelector(IERC20.transfer.selector, ...))` and only check that the low-level call did not revert, never inspecting the decoded boolean return value. Escrow accounting and the `_filled` finalization state are updated unconditionally, regardless of whether the underlying token transfer actually succeeded.

### Finding Description
`withdraw()` is invoked from `onAccept()` for `RedeemEscrow`/`RefundEscrow` requests and from `onGetResponse()` on GET-based cancellations [5](#0-4) . It performs the payout with:
```solidity
(bool success,) = token.call(abi.encodeWithSelector(IERC20.transfer.selector, beneficiary, amount));
if (!success) revert TransferFailed();
_orders[body.commitment][token] -= amount;
``` [6](#0-5) 
If the token contract returns `false` from `transfer()` (a legal ERC20/TRC20 behavior instead of reverting), `success` is still `true` because the *call* completed without reverting; only the ABI-decoded return payload would show failure, which is never checked. The same pattern recurs for fee release [3](#0-2)  and for `SweepDust` [2](#0-1) . Elsewhere in the same contract, inbound transfers correctly use `SafeERC20.safeTransferFrom` [4](#0-3) , confirming the outbound path is the inconsistent, unsafe one.

### Impact Explanation
Because the order/escrow state (`_filled`, `_orders[...][token]`) is committed regardless of the real transfer outcome, and the ISMP `RedeemEscrow`/`RefundEscrow`/GET-response commitment is single-use (replay-protected), a failed-but-non-reverting transfer permanently strands the escrowed tokens in the contract with no accounting entry left to reclaim them and no way for the beneficiary to be paid. This is a permanent freezing/loss of user and solver funds — meeting the High/Critical bar for concrete freezing of funds.

### Likelihood Explanation
This is triggered by the ordinary, unprivileged settlement flow (any solver filling an order, or any user cancelling via GET response) whenever the configured input/fee token exhibits non-reverting failure semantics on `transfer()` (a legal and common ERC20/TRC20 pattern, and especially plausible on Tron's TRC20 ecosystem which this file specifically targets). No attacker privilege is required — it can occur simply from routine token behavior (e.g., paused or restricted-transfer tokens), making it a reachable Medium-to-High likelihood issue for a production Tron deployment.

### Recommendation
Replace the raw `token.call(abi.encodeWithSelector(IERC20.transfer.selector, ...))` patterns in `withdraw()` and the `SweepDust` handler with `SafeERC20.safeTransfer()` (already imported and used elsewhere in the file), which validates both call success and the decoded boolean return value (or absence of return data per EIP-20 tolerance rules), consistent with the inbound `safeTransferFrom` usage.

### Proof of Concept
1. Deploy/whitelist an ERC20/TRC20-style token as an order's input token whose `transfer()` returns `false` on some failure path instead of reverting (e.g., a pausable or blacklist-enforcing token, or an intentionally non-conforming test token as used elsewhere in the test suite to model non-standard token behavior [7](#0-6) ).
2. User places an order escrowing this token via `placeOrder`.
3. Solver fills the order on the destination chain; the cross-chain `RedeemEscrow` message is delivered and `onAccept()` calls `withdraw()`.
4. Cause the token's `transfer()` to internally return `false` (e.g., toggle the paused/blacklist flag on the beneficiary right before settlement) so the call succeeds but no tokens are moved.
5. `withdraw()` observes `success == true`, decrements `_orders[commitment][token]`, and sets `_filled[commitment] = beneficiary` — finalizing the order with no tokens actually delivered and no remaining escrow entry to recover them, permanently freezing the funds in the contract.

### Citations

**File:** evm/tron/contracts/apps/IntentGatewayV2.sol (L404-406)
```text
                } else {
                    IERC20(token).safeTransferFrom(msg.sender, dispatcher, amount);
                }
```

**File:** evm/tron/contracts/apps/IntentGatewayV2.sol (L631-635)
```text
        if (kind == RequestKind.RedeemEscrow || kind == RequestKind.RefundEscrow) {
            authenticate(incoming.request);
            WithdrawalRequest memory body = abi.decode(incoming.request.body[1:], (WithdrawalRequest));
            return withdraw(body, kind == RequestKind.RefundEscrow);
        }
```

**File:** evm/tron/contracts/apps/IntentGatewayV2.sol (L661-681)
```text
        } else if (kind == RequestKind.SweepDust) {
            SweepDust memory req = abi.decode(incoming.request.body[1:], (SweepDust));

            uint256 outputsLen = req.outputs.length;
            for (uint256 i; i < outputsLen;) {
                TokenInfo memory info = req.outputs[i];
                address token = address(uint160(uint256(info.token)));
                uint256 amount = info.amount;

                if (token == address(0)) {
                    (bool sent,) = req.beneficiary.call{value: amount}("");
                    if (!sent) revert InsufficientNativeToken();
                } else {
                    (bool success,) = token.call(abi.encodeWithSelector(IERC20.transfer.selector, req.beneficiary, amount));
                    if (!success) revert TransferFailed();
                }
                unchecked {
                    ++i;
                }
                emit DustSwept(token, amount, req.beneficiary);
            }
```

**File:** evm/tron/contracts/apps/IntentGatewayV2.sol (L691-723)
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
        }
```

**File:** evm/tests/foundry/IntentGatewayV2SameChainTest.sol (L2714-2724)
```text
    function transfer(address to, uint256 amount) external returns (bool) {
        return _transfer(msg.sender, to, amount);
    }

    function transferFrom(address from, address to, uint256 amount) external returns (bool) {
        uint256 allowed = allowance[from][msg.sender];
        if (allowed != type(uint256).max) {
            allowance[from][msg.sender] = allowed - amount;
        }
        return _transfer(from, to, amount);
    }
```
