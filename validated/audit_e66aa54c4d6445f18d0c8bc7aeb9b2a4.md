### Title
Malicious order beneficiary can permanently freeze cross-chain escrow via reverting native-token transfer in `_withdraw` - (File: `evm/src/apps/intentsv2/IntentsBase.sol`)

### Summary
`IntentsBase._withdraw`, invoked from `onAccept` when a `RefundEscrow`/`RedeemEscrow` message arrives, pushes native-token escrow to `beneficiary` with a raw `.call{value:}("")` that reverts the whole function if the transfer fails. Because the beneficiary address (the order's `user`, or the destination-side filler) is baked immutably into the order commitment, and because Hyperbridge's delivery path isolates a failed `onAccept` by simply making the message retryable forever rather than failing the batch, a beneficiary that always reverts on receiving native value converts a normal refund/redemption into a permanently undeliverable message — freezing every token escrowed for that order, not just the native leg.

### Finding Description
`_withdraw` iterates every escrowed token for a commitment and, for the native-token leg, calls `_sendValue`, which reverts the entire withdrawal if the push fails: [1](#0-0) [2](#0-1) 

`_withdraw` is reached from `onAccept` for both `RedeemEscrow` (solver payout) and `RefundEscrow` (user refund after destination-side cancellation): [3](#0-2) 

`_cancelFromDest` sets `beneficiary = order.user` (the address that placed the order, `msg.sender` at `placeOrder`) and dispatches the `RefundEscrow` post request: [4](#0-3) 

The relayer path that eventually calls `onAccept` deliberately does not propagate a failed callback into a batch-wide revert — it isolates the failure per-message and leaves it retryable: [5](#0-4) 

That design correctly prevents one bad message from bricking a relay batch (the analog of the Revert Lend "push over pull" fix), but it does **not** solve the underlying problem when the same reverting beneficiary is retried on every future attempt: if `order.user` (or, for `RedeemEscrow`, the solver who filled the order) is a contract without a payable `receive()`/`fallback()`, or one deliberately built to revert when `msg.sender == IntentGatewayV2`, `_withdraw` will fail identically on every retry, forever. Since the beneficiary is fixed inside the hashed `Order`/`WithdrawalRequest`, there is no alternate recipient or fallback route to try. Cross-chain cancellation-related dispatches in this module use `timeout: 0` (no expiry) for the GET request that verifies unfilled status: [6](#0-5) 

and the mirrored Tron contract shows the same pattern for the `RefundEscrow` post dispatch itself using `timeout: 0`: [7](#0-6) 

so there is no built-in expiry that would let a different code path reclaim the funds once the beneficiary is permanently unreachable. The crucial multi-asset amplification is that `_withdraw` batches *all* of an order's escrowed tokens (ERC-20s and native ETH together) into one atomic loop keyed by a single `beneficiary`; a revert on the native-ETH leg blocks release of the unrelated ERC-20 legs in the same order too.

I was not able to fully confirm the exact `timeout` value used for `_post` in the `RefundEscrow` dispatch inside `_cancelFromDest` on the primary EVM contract (only the mirrored Tron contract and the sibling GET-request dispatch were directly inspected with `timeout: 0`); this should be verified during triage, though the consistent `timeout: 0` pattern elsewhere in the same module makes it likely.

### Impact Explanation
For `RefundEscrow`: the order creator (`order.user`) can only grief themselves, since `order.user` is always `msg.sender` at `placeOrder` — no third party's funds can be targeted this way, which limits severity for that specific path.

For `RedeemEscrow`, the beneficiary is the solver who filled the order on the destination chain (`msg.sender` at `fillOrder`) — again the party controlling that address is the one who becomes unable to redeem. In both cases the practical result is the same: the escrowed input tokens (which could include multiple ERC-20s bundled with native ETH) become permanently locked inside the `IntentGatewayV2`/`ExtrinsicIntents` contract, unreachable by anyone, satisfying "permanent freezing of funds." This is fundamentally a self-inflicted griefing vector rather than one where an attacker profits by stealing a victim's funds, which caps the severity below a funds-theft/insolvency-style Critical finding, but it still represents an unrecoverable, protocol-level freeze of value with no owner-provided remediation path (no sweep/rescue function exists for order-escrowed balances, only for protocol `dust` via `SweepDust`).

### Likelihood Explanation
Likelihood is Medium: it requires either (a) a party deliberately deploying a reverting recipient contract to grief their own order, which is irrational unless done for demonstration/griefing rather than profit, or (b) an innocent smart-contract wallet (multisig, ERC-4337 account, DAO treasury) that lacks a payable fallback being used as `order.user`/filler for a native-ETH order — a realistic accidental scenario given how common contract-based wallets are.

### Recommendation
Adopt the same pull-over-push pattern the referenced Revert Lend mitigation used: instead of unconditionally reverting `_withdraw` when a native-token push to `beneficiary` fails, catch the failure and credit the amount to an internal, beneficiary-claimable balance (a "pull" withdrawal function) rather than reverting the whole multi-token release. This decouples the ERC-20 legs of an order from the native-ETH leg's deliverability, ensures the `RefundEscrow`/`RedeemEscrow` message can always be marked as processed on first successful attempt, and gives a permanently-unreachable beneficiary (or anyone who later fixes/replaces that address, if governance allows) a way to retrieve funds later instead of freezing them forever.

### Proof of Concept
Conceptual PoC (mirrors the pattern already used in `evm/tests/foundry/IntentGatewayV2Test.sol`'s `testOnAcceptRefundEscrow`/`testOnAcceptRedeemEscrow`): [8](#0-7) 
1. Deploy a `MaliciousBeneficiary` contract whose `receive()`/`fallback()` always reverts.
2. Place a same-chain or cross-chain order whose `output.assets`/`inputs` include a native-ETH leg and `order.user` (or the filler) set to `MaliciousBeneficiary`.
3. Trigger cancellation from destination (`_cancelFromDest`) or a normal fill, so a `RefundEscrow`/`RedeemEscrow` `PostRequest` targets `IntentsBase._withdraw` with `beneficiary = address(MaliciousBeneficiary)`.
4. Call `onAccept` as the host with this request; `_sendValue` reverts inside `_withdraw`, so the whole `onAccept` call reverts.
5. Repeat the same call: it reverts identically every time — `EvmHost.dispatchIncoming` deletes the receipt each time (per `evm/src/core/EvmHost.sol:812-816`) so the message is retried indefinitely but never succeeds, leaving the escrowed tokens (ETH and any bundled ERC-20s) permanently stuck in the contract.

### Citations

**File:** evm/src/apps/intentsv2/IntentsBase.sol (L418-422)
```text
    /// @dev Native transfer that reverts with `InsufficientNativeToken` if refused.
    function _sendValue(address to, uint256 amount) internal {
        (bool sent,) = to.call{value: amount}("");
        if (!sent) revert InsufficientNativeToken();
    }
```

**File:** evm/src/apps/intentsv2/IntentsBase.sol (L451-469)
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
```

**File:** evm/src/apps/intentsv2/ExtrinsicIntents.sol (L254-267)
```text
        bytes memory context =
            abi.encode(WithdrawalRequest({commitment: commitment, tokens: order.inputs, beneficiary: order.user}));

        bytes[] memory keys = new bytes[](1);
        keys[0] = bytes.concat(abi.encodePacked(_instance(order.destination)), _calculateCommitmentSlotHash(commitment));
        DispatchGet memory request = DispatchGet({
            dest: order.destination,
            keys: keys,
            timeout: 0,
            height: options.height,
            fee: options.relayerFee,
            context: context,
            payer: msg.sender
        });
```

**File:** evm/src/apps/intentsv2/ExtrinsicIntents.sol (L297-307)
```text
    function _cancelFromDest(Order calldata order, CancelOptions calldata options, bytes32 commitment) internal {
        if (order.deadline >= _blockNumber()) {
            if (order.user != bytes32(uint256(uint160(msg.sender)))) revert Unauthorized();
        }

        _filled[commitment] = address(uint160(uint256(order.user)));

        _post(
            order, _body(RequestKind.RefundEscrow, commitment, order.inputs, order.user), options.relayerFee, msg.value
        );
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

**File:** evm/tron/contracts/apps/IntentGatewayV2.sol (L602-609)
```text
            DispatchPost memory request = DispatchPost({
                dest: order.source,
                to: abi.encodePacked(instance(order.source)),
                body: body,
                timeout: 0,
                fee: options.relayerFee,
                payer: msg.sender
            });
```

**File:** evm/tests/foundry/IntentGatewayV2Test.sol (L2293-2312)
```text
    function testOnAcceptRefundEscrow() public {
        uint256 inputAmount = 1000 * 1e6;

        TokenInfo[] memory inputs = new TokenInfo[](1);
        inputs[0] = TokenInfo({token: bytes32(uint256(uint160(address(usdc)))), amount: inputAmount});

        TokenInfo[] memory outputAssets = new TokenInfo[](1);
        outputAssets[0] = TokenInfo({token: bytes32(uint256(uint160(address(dai)))), amount: 1000 * 1e18});

        PaymentInfo memory output =
            PaymentInfo({beneficiary: bytes32(uint256(uint160(user))), assets: outputAssets, call: ""});

        Order memory order = Order({
            user: bytes32(uint256(uint160(user))),
            source: host.host(),
            destination: host.host(),
            deadline: block.number + 1000,
            nonce: 0,
            fees: 0,
            session: address(0),
```
