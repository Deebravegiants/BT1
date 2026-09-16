## Analog Found

### Title
Single misbehaving output/input token in a multi-token order permanently locks the entire order's escrow - ([File: evm/src/apps/intentsv2/IntentsBase.sol])

### Summary
`IntentsBase._withdraw` releases every token in a `WithdrawalRequest` inside one atomic loop with no per-token isolation. If any single token in that list becomes non-functional (blacklists the gateway, pauses, or self-destructs — the exact class of "collateral misbehaves unexpectedly" described in the referenced Reserve Protocol report), the whole withdrawal reverts and can never succeed again, permanently freezing every other, perfectly healthy token escrowed under the same order commitment.

### Finding Description
`_withdraw` iterates over `body.tokens` and calls `IERC20(token).safeTransfer(beneficiary, amount)` (or a native `.call`) for each entry in a single loop, decrementing `_orders[commitment][token]` as it goes: [1](#0-0) 

There is no try/catch around each token transfer — a revert on any single iteration reverts the whole function, exactly like `AssetRegistry.refresh()` looping over all collateral assets with no per-asset isolation in the original report. The two callers of `_withdraw`, `ExtrinsicIntents.onAccept` (for `RedeemEscrow`/`RefundEscrow`) and `IntrinsicIntents._cancelSameChain`, are permissionless/relayer-driven and will simply be resubmitted with the identical `WithdrawalRequest.tokens` array each time: [2](#0-1) 

`EvmHost.dispatchIncoming` was explicitly hardened against a *module-level* revert bricking the relayer's batch (it swallows a failing `onAccept` call and deletes the receipt so the message stays retryable) — this is the project's direct mitigation for the "single bad actor blocks everyone" bug class: [3](#0-2) 

However that mitigation only protects the *batch of unrelated messages*; it does nothing for the *contents of a single message*. Once `onAccept` is invoked for a specific `RedeemEscrow`/`RefundEscrow` request, `_withdraw`'s internal loop over that message's token list has no equivalent isolation. Every retry of the same commitment hits the same broken token at the same loop index and reverts identically, so the message is permanently undeliverable — the receipt is deleted and retried forever, but it can never succeed. Multi-token orders are an explicit, tested feature of the gateway: [4](#0-3) 

The Tron port has the identical pattern (`withdraw` in `IntentGatewayV2.sol`), looping per-token with a bare low-level `.call` and reverting the whole function on any single `TransferFailed`: [5](#0-4) 

### Impact Explanation
An order with N escrowed tokens where even one token becomes non-transferable (issuer blacklists the gateway/beneficiary, pauses transfers, gets upgraded to revert, or self-destructs — none of which require any Hyperbridge-side compromise) can never be redeemed or refunded. All escrow for that order, including tokens unrelated to the broken one, is permanently frozen: `RedeemEscrow` can't release it to the solver, `RefundEscrow` can't return it to the user, and same-chain `cancelOrder`/`_cancelSameChain` hits the same all-or-nothing loop. There is no admin/governance path in `IntentsBase`/`ExtrinsicIntents`/`IntrinsicIntents` to skip a single stuck token and release the rest — this is a concrete, permanent freezing of user and solver funds, matching the accepted "Medium/High" severity class of the original report.

### Likelihood Explanation
This requires no privileged or malicious protocol actor — only an ordinary ERC-20 with owner-controlled pause/blacklist/upgrade functionality (extremely common: USDC, USDT-style tokens) being included as one of several `TokenInfo` entries in an order's `inputs` or `output.assets`. A solver or user can trigger this unintentionally (their own token gets blacklisted/paused after order placement) or an attacker can construct a multi-token order using a token they control and intentionally break after escrow, DoS-locking co-escrowed legitimate tokens belonging to a counterparty.

### Recommendation
Make `_withdraw` resilient to a single failing token transfer, analogous to how `EvmHost.dispatchIncoming` isolates module-callback failures: wrap each token transfer in a try/catch (or low-level call with success check) and skip failed transfers while still decrementing/marking them for later retry, so that healthy tokens in the same order are always released even if one token is permanently broken. Alternatively, allow partial/per-token withdrawal requests so governance or the beneficiary can redeem the unaffected tokens independently of the stuck one.

### Proof of Concept
1. User places a same-chain (or cross-chain) order with two input tokens: `USDC` (healthy) and `TOKEN_X` (an ERC-20 the attacker/issuer controls), both escrowed via `IntentGatewayV2.placeOrder`.
2. After escrow, `TOKEN_X` is paused/blacklists the gateway address/self-destructs, so any `transfer`/`safeTransfer` call from the gateway reverts.
3. A solver fills the order, or the user cancels it; either path ultimately calls `_withdraw` with a `WithdrawalRequest.tokens` array containing both `USDC` and `TOKEN_X`.
4. The loop in `IntentsBase._withdraw` reaches `TOKEN_X`'s `safeTransfer` and reverts, rolling back the entire `_withdraw` call — including the `USDC` transfer that would otherwise have succeeded.
5. Every subsequent retry (resubmitted `RedeemEscrow`/`RefundEscrow`, or a fresh `cancelOrder` call) replays the identical token list and fails identically at the same index, so both `USDC` and `TOKEN_X` remain escrowed in the contract forever, with no function available to release the `USDC` portion alone.

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

**File:** evm/src/core/EvmHost.sol (L794-817)
```text
    function dispatchIncoming(PostRequest memory request, address relayer) external restrict(_hostParams.handler) {
        address destination = _bytesToAddress(request.to);
        uint256 size;
        assembly {
            size := extcodesize(destination)
        }
        if (size == 0) {
            // instead of reverting the entire batch, early return here.
            return;
        }

        // replay protection
        bytes32 commitment = request.hash();
        _requestReceipts[commitment] = relayer;

        (bool success,) = address(destination)
            .call(abi.encodeWithSelector(IApp.onAccept.selector, IncomingPostRequest(request, relayer)));

        if (!success) {
            // so that it can be retried
            delete _requestReceipts[commitment];
            return;
        }
        emit PostRequestHandled({commitment: commitment, relayer: relayer});
```

**File:** evm/tests/foundry/IntentGatewayV2SameChainTest.sol (L920-930)
```text
    function testSameChainSwap_MultiplePairs() public {
        // 1:1 pairing: USDC->ETH and DAI->USDC
        uint256 usdcInputAmount = 1000 * 1e6;
        uint256 daiInputAmount = 500 * 1e18;
        uint256 ethOutputAmount = 1 ether;
        uint256 usdcOutputAmount = 400 * 1e6;

        TokenInfo[] memory inputs = new TokenInfo[](2);
        inputs[0] = TokenInfo({token: bytes32(uint256(uint160(address(usdc)))), amount: usdcInputAmount});
        inputs[1] = TokenInfo({token: bytes32(uint256(uint160(address(dai)))), amount: daiInputAmount});

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
