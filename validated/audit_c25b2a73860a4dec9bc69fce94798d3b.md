### Title
Permanent freezing of Intent Gateway escrow when a solver, user, or fee-token beneficiary is blacklisted by an escrowed ERC-20 (e.g. USDC) - (File: `evm/src/apps/intentsv2/IntentsBase.sol`)

### Summary
`IntentsBase._withdraw()`, the single internal function used to release or refund all Intent Gateway escrow (fills, refunds, partial fills, cross-chain redemptions), iterates over every escrowed token for an order and unconditionally calls `safeTransfer` to a single `beneficiary` address, including a final `safeTransfer` of the accumulated relayer/protocol fee in the fee token. If any one of those tokens (commonly a blacklistable stablecoin such as USDC/USDT) refuses the transfer because the `beneficiary` is blacklisted, the whole function reverts, and **all** other tokens in the same withdrawal — not just the blacklisted one — fail to be released.

### Finding Description
`_withdraw` is the sole exit path for escrowed funds: [1](#0-0) 

and, when finalizing, it also force-transfers the accumulated fee-token balance to the same beneficiary: [2](#0-1) 

This function is reached from multiple unprivileged, permissionless entry points reachable by any user, solver, or relayer:
- Same-chain fills/partial-fills (`IntrinsicIntents.sol`) call `_withdraw` directly after a solver fills an order.
- Cross-chain settlement (`ExtrinsicIntents.sol`/`IntentGatewayV2.sol`) calls `_withdraw` from `onAccept`, which is itself invoked by `EvmHost.dispatchIncoming` when a relayer delivers a `RedeemEscrow`/`RefundEscrow` message: [3](#0-2) 

Crucially, `dispatchIncoming` treats a failed `onAccept` call as "retryable" by deleting the request receipt rather than permanently discarding the message: [4](#0-3) 

This "retry" mechanism does not help when the root cause is a blacklist: since the `WithdrawalRequest.beneficiary` (the solver address that filled the order, or the user for a refund) is embedded immutably in the committed order/settlement message, every retry of `onAccept` re-executes the exact same `_withdraw(beneficiary=blacklisted_address, ...)` call and reverts identically forever. There is no mechanism to redirect the beneficiary or to skip the blacklisted token and still release the others — the `for` loop has no per-token try/catch, so one blacklisted token halts release of every token (and the fee) in that commitment.

### Impact Explanation
- **Cross-chain fills**: if the solver address that filled an order becomes blacklisted by any one of the multiple escrowed input tokens before the `RedeemEscrow` message is processed on the source chain, that solver's entire escrowed input basket (potentially including non-blacklisted tokens) is permanently frozen — it can never be delivered, since every future relay attempt replays the same call and reverts.
- **Cancellations/refunds**: if the order's `user` becomes blacklisted by one of their own escrowed input tokens, their entire refund (all tokens in the order) is permanently locked with no recovery path, since `cancelOrder`/`_cancelFromSource`/`_cancelFromDest` all funnel into the same `_withdraw`.
- **Fee-token blacklist**: even if none of the primary escrowed tokens are blacklisted, if the beneficiary is blacklisted by the protocol's `feeToken` (used for relayer/solver fees), the fee `safeTransfer` at the tail of `_withdraw` reverts and blocks release of the otherwise-unaffected primary tokens too, because it all happens in a single atomic call.

This is a permanent freezing-of-funds condition (accepted impact category) triggered by a single relayed message/proof delivery from an unprivileged relayer or solver — no admin/governance action is required.

### Likelihood Explanation
Any solver or user interacting with the Intent Gateway across many EVM chains can be blacklisted on a centrally-controlled stablecoin (USDC, USDT) independent of Hyperbridge; nothing in the protocol prevents escrowing such tokens (test suite explicitly uses USDC as an escrowed input, e.g. `IntentGatewayV2Test.sol` `testOnAcceptRefundEscrow`/fill tests). Given regulatory blacklisting of addresses is an established real-world occurrence and the beneficiary address is chosen at order-fill time (potentially by an adversarial or targeted solver), the likelihood of this being triggered — accidentally or deliberately (e.g., a griefer registering as beneficiary for an order they know will be filled with a token the target is blacklisted on) — is meaningful, matching the "several reward/fund distribution processes" pattern in the referenced report.

### Recommendation
- In `_withdraw`, wrap each per-token transfer in a try/catch (or use a pull-payment pattern) so a failing transfer to one token does not block release of the others.
- For the fee-token transfer specifically, decouple it from the primary token release loop so a blacklisted beneficiary cannot block release of the underlying escrowed assets.
- Consider an escrow-to-claimable balance fallback: if a direct transfer fails, credit the beneficiary's claimable balance in that token so they (or a designated alternate address) can claim it later instead of bricking the whole settlement permanently.

### Proof of Concept
1. User places a cross-chain order on the source chain, escrowing `[USDC, DAI]` as inputs (as shown in `IntentGatewayV2Test.testOnAcceptRedeemEscrow`). [5](#0-4) 
2. Solver `S` fills the order on the destination chain, and the settlement `RedeemEscrow` message names `S` as `beneficiary`.
3. Before the message is relayed and processed on the source chain, `S` becomes blacklisted by the USDC contract (an event entirely outside Hyperbridge's control).
4. A relayer submits the proof; `HandlerV2.handlePostRequests` → `EvmHost.dispatchIncoming` → `IntentGatewayV2.onAccept` → `_withdraw` attempts `IERC20(USDC).safeTransfer(S, amount)` inside the loop in `IntentsBase.sol:451-470`, which reverts because `S` is blacklisted.
5. `dispatchIncoming` catches the revert and deletes the request receipt "so it can be retried" (`EvmHost.sol:812-816`), but every future retry replays the identical `_withdraw(beneficiary=S, ...)` call and reverts the same way — the escrowed USDC **and DAI** for this commitment are permanently unrecoverable.

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

**File:** evm/src/apps/intentsv2/IntentsBase.sol (L472-477)
```text
        if (finalize) {
            uint256 fees = _orders[body.commitment][TRANSACTION_FEES];
            if (fees > 0) {
                delete _orders[body.commitment][TRANSACTION_FEES];
                IERC20(IDispatcher(host()).feeToken()).safeTransfer(beneficiary, fees);
            }
```

**File:** evm/src/core/EvmHost.sol (L794-818)
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
    }
```

**File:** evm/tests/foundry/IntentGatewayV2Test.sol (L2258-2290)
```text
        vm.startPrank(user);
        usdc.approve(address(intentGateway), inputAmount);
        intentGateway.placeOrder(order, bytes32(0));
        vm.stopPrank();

        bytes32 commitment = keccak256(abi.encode(order));

        // Simulate RedeemEscrow request from IntentGateway on another chain
        bytes memory body = bytes.concat(
            bytes1(uint8(IntentsBase.RequestKind.RedeemEscrow)),
            abi.encode(
                WithdrawalRequest({
                    commitment: commitment, tokens: inputs, beneficiary: bytes32(uint256(uint160(filler)))
                })
            )
        );

        PostRequest memory request = PostRequest({
            source: host.host(),
            dest: host.host(),
            nonce: 0,
            from: abi.encodePacked(address(intentGateway)),
            to: abi.encodePacked(address(intentGateway)),
            body: body,
            timeoutTimestamp: 0
        });

        uint256 fillerBalanceBefore = usdc.balanceOf(filler);

        vm.prank(address(host));
        intentGateway.onAccept(IncomingPostRequest({relayer: relayer, request: request}));

        assertEq(usdc.balanceOf(filler) - fillerBalanceBefore, inputAmount, "Filler should receive escrowed tokens");
```
