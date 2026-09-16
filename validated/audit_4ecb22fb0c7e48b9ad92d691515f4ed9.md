### Title
Permanent freezing of escrowed funds when `_withdraw` beneficiary is blacklisted by the escrowed ERC20 (e.g. USDC) - ([File: evm/src/apps/intentsv2/IntentsBase.sol])

### Summary
`IntentsBase._withdraw()` unconditionally pushes escrowed ERC20 tokens to a `beneficiary` address via `IERC20(token).safeTransfer(beneficiary, amount)` with no fallback path. If the escrowed token is a blacklist-capable stablecoin (e.g. USDC/USDT) and the `beneficiary` (the user being refunded, or the solver being paid out) is blacklisted, this call reverts, and since `_withdraw` is invoked from the cross-chain `onAccept()` handler for `RedeemEscrow`/`RefundEscrow` messages as well as from same-chain fill/cancel paths, the revert either permanently blocks settlement of that specific order (locking the escrow forever) or, when reached through `onAccept`, causes the whole incoming Hyperbridge message delivery to revert.

### Finding Description
`_withdraw` is the single choke point releasing escrowed input tokens to a beneficiary for both fills and cancellations: [1](#0-0) 

This function is called from:
- `_cancelSameChain` (source-chain refund to `order.user`) [2](#0-1) 
- The `onAccept` handler processing `RedeemEscrow`/`RefundEscrow` cross-chain messages, releasing escrow to the solver or refunding the user, as documented in the settlement/cancellation flow [3](#0-2) , exercised in tests: [4](#0-3) 

Unlike the `WrappedHyperFungibleToken`/`WrappedHyperFungibleTokenUpgradeable` `onAccept`/`onPostRequestTimeout` handlers, which explicitly guard against a recipient unable to receive funds by falling back to wrapping ETH into WETH and delivering an ERC-20 transfer instead of reverting (a pattern the code comments explicitly call out as preventing "permanently lock[ing] funds for the same caller class") — [5](#0-4)  — `IntentsBase._withdraw` has no such fallback for ERC20 transfers. It performs a bare `safeTransfer` to `beneficiary` with no alternate-address or pull-based recovery mechanism: [6](#0-5) 

Because USDC (and similarly-featured stablecoins) implement address blacklisting at the `transfer`/`transferFrom` level, a `beneficiary` that becomes blacklisted between order placement and settlement will cause `safeTransfer` to revert unconditionally.

### Impact Explanation
For the cross-chain path, this transfer happens inside the message-delivery handler `onAccept`, which is invoked by the ISMP host when relaying the `RedeemEscrow`/`RefundEscrow` POST request. A revert here means the incoming cross-chain settlement message cannot be delivered at all — the escrowed input tokens on the source chain remain locked in the `IntentGateway` contract indefinitely, since:
1. The order is already marked filled/cancelled on the destination chain (irreversible), so the order cannot be re-filled or re-cancelled through the normal path.
2. `_orders[commitment][token]` is only decremented on a successful `_withdraw` call, so escrow is stuck at its pre-decrement value with no other function in the contract to sweep or redirect it to an alternate address.
This is a direct, permanent loss of escrowed user/solver funds, matching High/Medium severity for locked-funds bugs, and is fully reachable by an ordinary permissionless intents user/solver interaction (placing an order, then that beneficiary being blacklisted before settlement finalizes) — no privileged actor is required.

### Likelihood Explanation
Likelihood is realistic given that popular assets explicitly named as compatible with the intents system (e.g. USDC, used throughout the test suite as the escrowed input token) implement blacklisting, and blacklisting events are outside the protocol's control (regulatory action, OFAC-driven freezes, exchange compliance actions). Any user or solver whose address gets blacklisted while their order is in flight — a scenario outside their control and unrelated to protocol misbehavior — triggers the freeze deterministically on the very next fill/cancel/settlement attempt.

### Recommendation
Add a fallback path in `_withdraw` (and analogous escrow-release call sites) so that a failed `safeTransfer` to `beneficiary` does not brick the entire withdrawal: e.g. wrap the transfer in a try/catch and, on failure, credit the amount to a pull-based claimable balance mapping that the beneficiary (or a designated alternate address) can withdraw later, mirroring the resilience pattern already used in `WrappedHyperFungibleToken`'s native-transfer fallback.

### Proof of Concept
1. User places a cross-chain order escrowing USDC as input via `placeOrder`, with `beneficiary`/`order.user` = address `A`.
2. Address `A` becomes blacklisted by USDC's issuer (e.g., flagged for illicit activity) before the order settles.
3. A solver fills the order on the destination chain; the `RedeemEscrow`/`RefundEscrow` message is relayed back to the source chain and delivered via `onAccept` → `_withdraw`.
4. `IERC20(USDC).safeTransfer(A, amount)` in `_withdraw` (evm/src/apps/intentsv2/IntentsBase.sol:468) reverts because `A` is blacklisted.
5. The message delivery reverts; `_orders[commitment][USDC]` is never decremented, and the escrowed USDC is permanently stuck in the `IntentGateway` contract with no alternate recovery function, matching the reachable analog of the original report's blacklist-freeze bug class.

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

**File:** evm/src/apps/intentsv2/IntrinsicIntents.sol (L159-180)
```text
    function _cancelSameChain(Order calldata order, bytes32 commitment) internal {
        if (order.user != bytes32(uint256(uint160(msg.sender)))) revert Unauthorized();

        uint256 inputsLen = order.inputs.length;
        TokenInfo[] memory remainingTokens = new TokenInfo[](inputsLen);
        bool hasEscrow = false;
        for (uint256 i; i < inputsLen;) {
            address token = address(uint160(uint256(order.inputs[i].token)));
            uint256 escrowed = _orders[commitment][token];
            if (escrowed > 0) hasEscrow = true;
            remainingTokens[i] = TokenInfo({token: order.inputs[i].token, amount: escrowed});
            unchecked {
                ++i;
            }
        }
        if (!hasEscrow) revert UnknownOrder();

        WithdrawalRequest memory body =
            WithdrawalRequest({commitment: commitment, tokens: remainingTokens, beneficiary: order.user});

        _withdraw(body, true, true);
    }
```

**File:** docs/content/developers/evm/intent-gateway/overview.mdx (L50-69)
```text
### Settlement

When the settlement message arrives on the source chain, the ISMP host calls `onAccept()`. The handler authenticates the message (verifying it came from a known IntentGateway instance), decodes the `WithdrawalRequest`, and calls `withdraw()` which:

1. Marks the order as filled (`_filled[commitment] = solver`)
2. Transfers each escrowed input token to the solver
3. Releases stored transaction fees (in fee token) to the solver
4. Emits `EscrowReleased(commitment, tokens)`

### Cancellation

There are two modes for cross-chain cancellation:

`cancelOrder` emits `OrderCancelled(commitment, canceller)` on the chain the cancellation is initiated from, before it routes to either path below. `EscrowRefunded` remains the terminal event, on the source chain, once the escrow is actually returned.

**Cancel from source chain**: The user calls `cancelOrder()` on the source chain, which dispatches a `DispatchGet` storage read request to query the destination chain's fill status. The `CancelOptions.height` must be greater than `order.deadline` — this ensures the proof is taken from a block after the order has expired. A relayer processes this request on Hyperbridge by providing storage proofs from the destination chain. If the storage slot for `_filled[commitment]` is empty (order unfilled), Hyperbridge dispatches a response back to the source chain. The `onGetResponse` handler verifies the empty proof and calls `withdraw()` to refund the escrowed tokens to the user. If the order was filled, the response contains a non-empty value and the handler reverts with `Filled()`.

![Cancel from Source Chain](./images/intent-gateway-cancel-source.svg)

**Cancel from destination chain**: Before the deadline, only the order owner can call `cancelOrder()` on the destination chain. After the deadline, anyone can cancel. The function marks the order as cancelled locally (`_filled[commitment] = user`) to prevent future fills, then dispatches a cross-chain `RefundEscrow` message back to the source chain. When the source chain receives this message via `onAccept()`, it calls `withdraw()` to refund the escrowed tokens to the user and emits `EscrowRefunded(commitment, tokens)`.
```

**File:** evm/tests/foundry/IntentGatewayV2Test.sol (L2275-2291)
```text
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
    }
```

**File:** sdk/packages/core/contracts/apps/WrappedHyperFungibleToken.sol (L309-324)
```text
        if (_isWeth) {
            // Try a native-ETH push first (cheap for EOAs and payable contracts);
            // if the recipient cannot accept native value (no `receive()` / `fallback()
            // payable`), re-wrap the withdrawn ETH and deliver the underlying WETH as
            // an ERC-20 transfer instead. This mirrors the deposit-side flexibility of
            // `send()` (which accepts WETH from non-payable callers via `safeTransferFrom`)
            // so the refund path doesn't permanently lock funds for the same caller class.
            IWETH(_underlying).withdraw(message.amount);
            (bool sent,) = beneficiary.call{value: message.amount}("");
            if (!sent) {
                IWETH(_underlying).deposit{value: message.amount}();
                IERC20(_underlying).safeTransfer(beneficiary, message.amount);
            }
        } else {
            IERC20(_underlying).safeTransfer(beneficiary, message.amount);
        }
```
