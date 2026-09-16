### Title
Blacklisted `order.user`/beneficiary permanently bricks escrow refund and release in IntentGatewayV2 (`_withdraw`) - (File: `evm/src/apps/intentsv2/IntentsBase.sol`)

### Summary
`IntentsBase._withdraw` pushes escrowed ERC20 tokens directly to a hardcoded beneficiary address via `IERC20(token).safeTransfer(beneficiary, amount)` with no fallback if the transfer reverts (e.g., token issuer blacklists the recipient, as with USDC/USDT). Because the beneficiary for refunds is fixed at order-placement time (`order.user`) and cannot be changed by the user, a blacklisted user can never recover their escrowed collateral — the same root-cause pattern as the referenced Sherlock report against Surge's `Pool.removeCollateral()`.

### Finding Description
`_withdraw` decrements `_orders[commitment][token]` and then immediately calls `IERC20(token).safeTransfer(beneficiary, amount)` in the same transaction: [1](#0-0) 

If `safeTransfer` reverts (the collateral/input token blacklists `beneficiary`), the entire call reverts, rolling back the escrow decrement — so the funds remain locked in `_orders[commitment][token]` and the operation can be retried indefinitely, always reverting for the same reason, because the beneficiary is not user-selectable.

This is reachable through the intents escrow paths listed as in-scope:
- Same-chain cancel: beneficiary is hardcoded to `order.user`, the original order creator, with no way to redirect funds to another address: [2](#0-1) 
- Cross-chain cancel-from-destination: dispatches a `RefundEscrow` message whose `WithdrawalRequest.beneficiary` is fixed to `order.user`: [3](#0-2) 
- Cross-chain cancel-from-source (GET-response path) also fixes `beneficiary` to `order.user`, and both `onAccept` (`RedeemEscrow`/`RefundEscrow`) and `onGetResponse` invoke `_withdraw` with no way to substitute the recipient: [4](#0-3) [5](#0-4) 

Since `order.user` is bound at `placeOrder` time and immutable thereafter, if the account is later blacklisted by the input token's issuer (a scenario explicitly relevant for USDC/USDT-class tokens used as intent inputs), every refund/redeem path for that specific order commitment permanently reverts. There is no pull-based withdrawal fallback (unlike the native-ETH path elsewhere in the codebase, e.g. `WrappedHyperFungibleToken.onAccept`, which falls back to wrapping ETH if a raw call fails — no equivalent fallback exists here for ERC20 transfers to a blacklisted beneficiary).

### Impact Explanation
A user whose address becomes blacklisted by the input ERC20 token (common practice for USDC/USDT under sanctions/compliance actions) permanently loses access to their escrowed input tokens for any pending or cancellable order. The tokens remain locked in the `IntentGatewayV2` contract's escrow accounting (`_orders` mapping) with no path to recovery — not by the user, not by governance (there is no override function to redirect an individual order's beneficiary), and not by a pull-payment mechanism. This is a permanent freezing of user funds, satisfying the "permanent freezing of funds" criterion for the intents escrow attack surface.

### Likelihood Explanation
The trigger requires only that the token used as an order input places the affected address on a blacklist after (or even before, if manipulated) escrow, which is an established real-world occurrence for regulated stablecoins (OFAC-driven USDC/USDT blacklisting events have happened repeatedly). No malicious governance/admin/relayer action is needed — a single external event (blacklisting) combined with the user's own prior `placeOrder`/`cancelOrder` transaction is sufficient to trigger permanent lock, matching the analog bug class exactly.

### Recommendation
Add a pull-based withdrawal fallback for ERC20 transfers in `_withdraw` (and `_sweepDust`): on `safeTransfer` failure, credit the amount to an internal `pendingWithdrawals[beneficiary][token]` balance (rather than reverting the whole state transition) and expose a separate `claim(token, recipient)` function that lets the beneficiary designate an alternate, non-blacklisted receiving address. Alternatively, allow the order creator to specify/update a recipient address distinct from `order.user` for refund purposes.

### Proof of Concept
1. User places a same-chain order via `IntrinsicIntents`/`IntentGatewayV2` using a blacklist-capable ERC20 (e.g. USDC) as `order.inputs[0].token`; tokens are escrowed under `_orders[commitment][token]`.
2. Before the order is filled, the token issuer blacklists the user's address (`order.user`) for a compliance reason unrelated to Hyperbridge.
3. After the order deadline, the user (or anyone, post-deadline for cross-chain) calls `cancelOrder`, which routes to `_cancelSameChain` / `_cancelFromDest` / `_cancelFromSource`, eventually invoking `IntentsBase._withdraw` with `beneficiary = order.user`.
4. `IERC20(token).safeTransfer(beneficiary, amount)` reverts because `beneficiary` is blacklisted by the token contract.
5. The entire transaction reverts; `_orders[commitment][token]` is never decremented. Every subsequent cancel attempt reverts identically since the beneficiary is immutable — the escrowed tokens are permanently frozen in the `IntentGatewayV2` contract.

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

**File:** evm/src/apps/intentsv2/ExtrinsicIntents.sol (L240-275)
```text
    function _cancelFromSource(Order calldata order, CancelOptions calldata options, bytes32 commitment) internal {
        if (order.user != bytes32(uint256(uint160(msg.sender)))) revert Unauthorized();

        if (options.height <= order.deadline) revert NotExpired();

        uint256 inputsLen = order.inputs.length;
        for (uint256 i; i < inputsLen;) {
            if (_orders[commitment][address(uint160(uint256(order.inputs[i].token)))] == 0) revert UnknownOrder();

            unchecked {
                ++i;
            }
        }

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

        address hostAddr = host();
        if (msg.value > 0) {
            IDispatcher(hostAddr).dispatch{value: msg.value}(request);
        } else {
            dispatchWithFeeToken(request);
        }
    }
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

**File:** evm/src/apps/intentsv2/ExtrinsicIntents.sol (L330-366)
```text
    function onAccept(IncomingPostRequest calldata incoming) external override onlyHost {
        _checkRelayer(incoming.relayer);
        RequestKind kind = RequestKind(uint8(incoming.request.body[0]));
        if (kind == RequestKind.RedeemEscrow || kind == RequestKind.RefundEscrow) {
            _authenticate(incoming.request);
            WithdrawalRequest memory body = abi.decode(incoming.request.body[1:], (WithdrawalRequest));
            return _withdraw(body, kind == RequestKind.RefundEscrow, true);
        }

        // only hyperbridge is permitted to perform these actions
        if (keccak256(incoming.request.source) != keccak256(IDispatcher(host()).hyperbridge())) revert Unauthorized();
        if (kind == RequestKind.NewDeployment) {
            _addDeployment(abi.decode(incoming.request.body[1:], (Deployment)));
        } else if (kind == RequestKind.UpdateParams) {
            _updateParams(abi.decode(incoming.request.body[1:], (ParamsUpdate)));
        } else if (kind == RequestKind.SweepDust) {
            _sweepDust(abi.decode(incoming.request.body[1:], (SweepDust)));
        } else if (kind == RequestKind.Execute) {
            Address.functionDelegateCall(ERC1967Utils.getImplementation(), incoming.request.body[1:]);
        }
    }

    /**
     * @dev Handles the response to a Hyperbridge GET request dispatched during
     * `_cancelFromSource`. Verifies that the `_filled` storage slot on the destination
     * chain is empty (meaning the order was never filled), then refunds the escrowed
     * tokens to the original user. Reverts with `Filled` if the slot is non-empty.
     *
     * @param incoming The incoming GET response from Hyperbridge containing the storage proof.
     */
    function onGetResponse(IncomingGetResponse calldata incoming) external override onlyHost {
        _checkRelayer(incoming.relayer);
        if (incoming.response.values[0].value.length != 0) revert Filled();

        WithdrawalRequest memory body = abi.decode(incoming.response.request.context, (WithdrawalRequest));
        _withdraw(body, true, true);
    }
```
