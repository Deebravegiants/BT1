### Title
Malicious escrow token can permanently freeze co-escrowed legitimate assets in `IntentGatewayV2`'s multi-token `_withdraw` - (File: evm/src/apps/intentsv2/IntentsBase.sol)

### Summary
`IntentsBase._withdraw` (and its analog in `evm/tron/contracts/apps/IntentGatewayV2.sol`) releases all escrowed tokens for an order commitment in a single loop. Any user placing an order can pick an arbitrary ERC-20-like input token — there is no token whitelist in the intent gateway. A token that reverts on transfer to a specific recipient (the classic ERC-777 `tokensReceived`-revert pattern from the referenced report, or any malicious/"poison" ERC-20 with a conditional revert) will cause the entire withdrawal transaction to revert, including transfers of the other, legitimate tokens bundled in the same order/commitment.

### Finding Description
`_withdraw` iterates over `body.tokens` and transfers each one to the beneficiary: [1](#0-0) 
and, for the low-level-call variant used in the Tron contract, treats a failed `call` as a hard revert via `TransferFailed()`: [2](#0-1) 

Because `_filled[body.commitment]`/`withdraw`'s state mutation happens inside the same atomic call as the token transfer loop, if *any* one of the tokens in `body.tokens` reverts on transfer (e.g., an ERC-777-style token whose recipient-side hook the attacker controls, or a token contract that simply reverts for a chosen recipient), the whole `withdraw`/`_withdraw` call reverts and rolls back — including the release of every *other*, non-malicious token that was escrowed for that same commitment. There is no per-token try/catch or isolation, and no token whitelist gate anywhere in `IntentGatewayV2`/`IntentsBase` restricting which ERC-20 addresses can be used as `order.inputs`/`order.outputs`/consideration assets when `placeOrder` is called.

Since the same commitment/withdrawal path (`RedeemEscrow`/`RefundEscrow`, or `onGetResponse`) is the only route to release the escrow, and it will deterministically revert every time it's invoked (the malicious token's revert condition doesn't change), the escrowed legitimate assets for that order become permanently stuck — mirroring the reNFT ERC-777 `tokensReceived`-revert DoS, but here the "poison" asset doesn't even need to be a real ERC-777; any transfer-reverting ERC-20 impersonator selected by the order creator suffices, and the blast radius extends to all tokens bundled in the same order.

### Impact Explanation
This results in permanent freezing of legitimate escrowed funds (other users' or the same order's non-malicious token legs) with no code path to selectively skip or force through the poisoned token and still release the rest. This satisfies "permanent freezing of funds" impact and is reachable directly by any unprivileged user who calls `placeOrder` with a crafted token as one of the order's assets — no privileged role is required.

### Likelihood Explanation
Likelihood is moderate-to-high: an attacker only needs to deploy a trivial ERC-20-compatible contract whose `transfer`/`transferFrom` to a chosen address reverts (no real ERC-777 registration or ERC-1820 interaction needed for this variant since the gateway does a raw `token.call` / `safeTransfer` regardless of token standard), then place an order pairing this token with valuable legitimate tokens. Any solver/filler who unknowingly fills such an order, or any process that triggers `RedeemEscrow`/`RefundEscrow` for that commitment, will hit the same revert, permanently blocking release of the escrow.

### Recommendation
- Introduce an allow-list/whitelist of tokens that can be used as `order.inputs`/`order.outputs` in `IntentGatewayV2`, mirroring the mitigation reNFT ultimately adopted for the analogous finding.
- Alternatively/additionally, make `_withdraw`/`withdraw` resilient per-token: use a bounded-gas, try/catch (or a "pull" pattern where failed transfers credit an internal balance the beneficiary can later claim) so that one poisoned token cannot block release of the other escrowed assets tied to the same commitment.
- Ensure the same isolation applies to `IntentGatewayV2.sol` (EVM) and the Tron variant's `withdraw` function, which uses the same non-isolated loop-and-revert pattern.

### Proof of Concept
1. Attacker deploys `PoisonToken`, an ERC-20 whose `transfer(to, amount)` reverts whenever `to == <specific solver/relayer address>` (or unconditionally, since the attacker can choose to fill it themselves).
2. Attacker calls `placeOrder` with `order.inputs = [PoisonToken (amount X), USDC (amount Y)]`, escrowing both tokens into the gateway.
3. A solver fills the order cross-chain/same-chain; a `RedeemEscrow` request is eventually delivered (via `onAccept`) or a GET response triggers `onGetResponse`, both of which call `withdraw`/`_withdraw` with `body.tokens = [PoisonToken, USDC]`. [3](#0-2) 
4. Inside `withdraw`, the loop attempts `PoisonToken.call(transfer(...))` first (or interleaved); it fails, and `TransferFailed()` reverts the entire call, rolling back the USDC release along with it.
5. Every subsequent retry of the same withdrawal for this commitment hits the identical poisoned transfer and reverts, permanently freezing the escrowed USDC (and PoisonToken) for that order — no other path exists in the contract to selectively withdraw the non-poisoned token. [1](#0-0)

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

**File:** evm/tron/contracts/apps/IntentGatewayV2.sol (L631-635)
```text
        if (kind == RequestKind.RedeemEscrow || kind == RequestKind.RefundEscrow) {
            authenticate(incoming.request);
            WithdrawalRequest memory body = abi.decode(incoming.request.body[1:], (WithdrawalRequest));
            return withdraw(body, kind == RequestKind.RefundEscrow);
        }
```

**File:** evm/tron/contracts/apps/IntentGatewayV2.sol (L691-714)
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
```
