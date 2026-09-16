### Title
Order input funded with an ERC721 (or other non-ERC20-compliant) token permanently bricks escrow withdrawal, freezing the solver's already-delivered funds - ([File: evm/src/apps/IntentGatewayV2.sol])

### Summary
`IntentGatewayV2.placeOrder` accepts an arbitrary, unwhitelisted `token` address for every order input and escrows it using only the generic ERC20 `transferFrom`/`balanceOf` selectors, which are selector-identical to ERC721's `transferFrom`/`balanceOf`. An order creator can therefore "fund" an input with an ERC721 token they own. The deposit succeeds, but the later payout path (`_withdraw`, used by both `RedeemEscrow` and `RefundEscrow`) calls `safeTransfer` (`transfer(address,uint256)`), a function ERC721 does not implement, causing a permanent revert. This mirrors the OpenQ `H-2` bug class: a generic receive function accepts a token type whose payout function is incompatible, permanently bricking the escrow.

### Finding Description
In the non-predispatch branch of `placeOrder`, each input token is pulled with generic ERC20 calls and no type/whitelist check: [1](#0-0) 

`IERC20(token).safeTransferFrom(msg.sender, address(this), order.inputs[i].amount)` uses selector `0x23b872dd`, identical to ERC721's `transferFrom(address,address,uint256)`. If the attacker (the order creator) owns an ERC721 token with `tokenId == order.inputs[i].amount` and has approved the gateway, this call succeeds and returns no data — which `safeTransferFrom`'s success check (`returndata.length == 0 || abi.decode(returndata,(bool))`) accepts. The subsequent `balanceOf(address(this))` diff (ERC721's NFT count, not an ERC20 amount) is then written back into `order.inputs[i].amount` and used to build the commitment and escrow accounting, with no validation that the token behaves like an ERC20.

When the order is later settled — either a same-chain fill, a cross-chain `RedeemEscrow` after the solver has already delivered output tokens on the destination chain, or a `RefundEscrow`/cancellation — the escrowed "amount" is paid out via `_withdraw`: [2](#0-1) 

`IERC20(token).safeTransfer(beneficiary, amount)` calls selector `0xa9059cbb` (`transfer(address,uint256)`), which does not exist on ERC721. The call has no matching function and reverts, causing `_withdraw` to revert unconditionally for that token — and because `_withdraw` loops over *all* tokens in `body.tokens` in a single transaction, a single poisoned ERC721 entry blocks release of every other (legitimate ERC20) token escrowed for the same order commitment.

For the cross-chain path, this same `_withdraw` is reached through `onAccept` handling `RequestKind.RedeemEscrow`/`RefundEscrow`: [3](#0-2) 

Since `_fillCrossChain` already transferred real output tokens to the beneficiary *before* dispatching the `RedeemEscrow` message that would repay the solver: [4](#0-3) 

a solver who fills such a poisoned order irrevocably loses the value they paid out, because the settlement message that would release the escrowed input back to them can never succeed.

### Impact Explanation
This permanently freezes funds:
- Any ERC20 input tokens escrowed alongside the poisoned ERC721 in the same order become permanently unwithdrawable (the `_withdraw` loop reverts on the ERC721 leg before or after processing the ERC20 legs, and there is no per-token try/catch or skip logic).
- On cross-chain orders, a solver who fills the order in good faith delivers real value to the beneficiary on the destination chain, then can never redeem the escrowed input on the source chain because `RedeemEscrow` processing (`onAccept` → `_withdraw`) reverts forever. This is a direct, unrecoverable loss of solver funds — an unprivileged actor (intent solver) explicitly in scope.
- Same-chain cancellation/refund is likewise permanently blocked for the affected commitment, locking the user's own remaining escrow too.

This satisfies "permanent freezing of funds" and, for the solver, "concrete theft" of already-delivered value.

### Likelihood Explanation
No privileged access is required. Any user can place an order (`placeOrder` is public/unpermissioned) and can freely choose any `token` address for `order.inputs[i].token`, including an ERC721 contract they own and have approved to the gateway. There is no ERC20 whitelist or type check on input tokens in `IntentGatewayV2`/`IntentsBase`, so triggering the deposit half of the bug is trivial and requires only owning one NFT and calling `placeOrder`.

### Recommendation
- Validate that input tokens implement ERC20 semantics before accepting them as escrow, e.g., require a nonzero `totalSupply()`/`decimals()` response, or restrict order inputs to an explicit ERC20 token whitelist as OpenQ ultimately did.
- Alternatively, harden `_withdraw` to use low-level calls with explicit success/selector checks per token and allow partial success (skip and flag a broken token) rather than reverting the entire batch, so a single malformed token cannot freeze co-escrowed legitimate assets.
- Reject the order at placement time when `IERC20(token).balanceOf(address(this))` diff doesn't match the literal `transferFrom` amount requested (currently silently overwritten), which would surface ERC721-style responses immediately instead of only failing at payout time.

### Proof of Concept
1. Attacker deploys/owns an ERC721 NFT with `tokenId = N` and calls `approve(intentGateway, N)` (or `setApprovalForAll`).
2. Attacker calls `placeOrder` with `order.inputs[0] = { token: <ERC721 address>, amount: N }` (same-chain or cross-chain, optionally bundling a legitimate ERC20 leg in the same order to maximize damage).
3. `placeOrder`'s `safeTransferFrom(msg.sender, address(this), N)` succeeds because ERC721's `transferFrom` shares the ERC20 selector and returns no data. `balanceOf(address(this))` diff (1) is stored as the escrowed "amount".
4. Order proceeds to be filled (same-chain) or filled cross-chain by a solver who delivers real output tokens to the beneficiary, then `RedeemEscrow` is dispatched back to the source chain.
5. `_withdraw` attempts `IERC20(nft).safeTransfer(beneficiary, 1)`; the call reverts because ERC721 has no `transfer(address,uint256)` function.
6. The transaction (same-chain fill/cancel, or `onAccept` processing of `RedeemEscrow`/`RefundEscrow`) reverts permanently — the escrow (including any co-escrowed ERC20 legs) can never be released, and any solver who already delivered output value on the destination chain can never be repaid.

### Citations

**File:** evm/src/apps/IntentGatewayV2.sol (L312-329)
```text
        } else {
            for (uint256 i; i < inputsLen;) {
                if (order.inputs[i].amount == 0) revert InvalidInput();
                address token = address(uint160(uint256(order.inputs[i].token)));
                if (token == address(0)) {
                    if (msgValue < order.inputs[i].amount) revert InsufficientNativeToken();
                    msgValue -= order.inputs[i].amount;
                } else {
                    uint256 balBefore = IERC20(token).balanceOf(address(this));
                    IERC20(token).safeTransferFrom(msg.sender, address(this), order.inputs[i].amount);
                    order.inputs[i].amount = IERC20(token).balanceOf(address(this)) - balBefore;
                }

                unchecked {
                    ++i;
                }
            }
        }
```

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

**File:** evm/src/apps/intentsv2/ExtrinsicIntents.sol (L186-219)
```text
            if (token == address(0)) {
                if (msgValue < solverAmount) revert InsufficientNativeToken();
                uint256 beneficiaryTotal = totalRequired + beneficiaryShare;
                _sendValue(beneficiary, beneficiaryTotal);
                msgValue -= (beneficiaryTotal + protocolShare);
            } else {
                IERC20(token).safeTransferFrom(msg.sender, beneficiary, totalRequired + beneficiaryShare);
                if (protocolShare > 0) {
                    IERC20(token).safeTransferFrom(msg.sender, address(this), protocolShare);
                }
            }
            if (protocolShare > 0) emit DustCollected(token, protocolShare);
            outputFills[i] = TokenInfo({token: outputToken, amount: totalRequired});
        }

        _execute(order, outputsLen);

        // Native dispatch fee only if the solver sent enough to cover it; else the fee token.
        uint256 nativeFee = options.nativeDispatchFee;
        if (nativeFee > msgValue) nativeFee = 0;
        msgValue -= nativeFee;
        _post(
            order,
            _body(RequestKind.RedeemEscrow, commitment, order.inputs, bytes32(uint256(uint160(msg.sender)))),
            options.relayerFee,
            nativeFee
        );

        // Refund any unspent native tokens to the solver.
        if (msgValue > 0) {
            _sendValue(msg.sender, msgValue);
        }

        emit OrderFilled({commitment: commitment, filler: msg.sender, outputs: outputFills, inputs: order.inputs});
```

**File:** evm/src/apps/intentsv2/ExtrinsicIntents.sol (L330-337)
```text
    function onAccept(IncomingPostRequest calldata incoming) external override onlyHost {
        _checkRelayer(incoming.relayer);
        RequestKind kind = RequestKind(uint8(incoming.request.body[0]));
        if (kind == RequestKind.RedeemEscrow || kind == RequestKind.RefundEscrow) {
            _authenticate(incoming.request);
            WithdrawalRequest memory body = abi.decode(incoming.request.body[1:], (WithdrawalRequest));
            return _withdraw(body, kind == RequestKind.RefundEscrow, true);
        }
```
