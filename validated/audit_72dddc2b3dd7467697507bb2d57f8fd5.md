I have enough evidence to confirm this analog. The `_withdraw` function in `IntentsBase.sol` performs unconditional `safeTransfer`/`safeTransferFrom`-style releases to a `beneficiary` address with no per-token isolation or pull-payment fallback, and `SweepDust`/governance functions only cover protocol dust, not stuck escrow — there is no recovery path for a beneficiary that becomes unable to receive one of the escrowed tokens.

### Title
Permanent freezing of escrowed order funds when a beneficiary is blocklisted by one of the escrowed ERC20 tokens (e.g. USDC) - ([File: evm/src/apps/intentsv2/IntentsBase.sol])

### Summary
`IntentsBase._withdraw`, invoked from `onAccept`/`onGetResponse` on `RedeemEscrow`, `RefundEscrow`, and same-chain cancel paths, iterates over all escrowed tokens for an order and unconditionally calls `IERC20.safeTransfer(beneficiary, amount)` for each one, and additionally forwards accumulated `TRANSACTION_FEES` to the same beneficiary. If any single one of these transfers reverts — most notably because the token is a blocklisting stablecoin (e.g. USDC) and the beneficiary address is or becomes blocklisted — the entire `_withdraw` call reverts, permanently blocking release of *all* tokens escrowed for that order commitment, not just the blocklisting one.

### Finding Description
`_withdraw` in `evm/src/apps/intentsv2/IntentsBase.sol` is the single settlement primitive for cross-chain intent orders: [1](#0-0) 

It is reached via a single dispatched ISMP message (an unprivileged relayer-delivered `RedeemEscrow`/`RefundEscrow` POST request, or a `GetResponse` for source-chain cancellation): [2](#0-1) 

There is no try/catch, no per-token isolation, and no pull-payment escape hatch: a single failing `safeTransfer` (e.g. USDC's `transfer` reverting because `beneficiary` is on its blocklist) causes the whole function — and therefore the whole `onAccept`/`onGetResponse` call — to revert. Because `EvmHost.dispatchIncoming` merely deletes the request receipt and returns on a failed `onAccept` call so the message can be retried later, the message is retryable forever but will never succeed while the beneficiary remains blocklisted, since retrying invokes the exact same reverting transfer: [3](#0-2) 

This directly mirrors the referenced Cooler.sol bug class: an unprivileged/external condition (a token issuer blocklisting an address) on a shared debt-settlement code path with no fallback locks funds for parties who did nothing wrong. Here, all input tokens escrowed for an order (which can include non-blocklisting tokens too, per `TokenInfo[] inputs`) become permanently unrecoverable in the same transaction as soon as one of them is a blocklisting token and the beneficiary is denylisted for it. This affects:
- The solver/filler beneficiary on `RedeemEscrow` (`ExtrinsicIntents._fillCrossChain` / `IntrinsicIntents` fill paths).
- The order's original user on `RefundEscrow` / cancellation paths (`_cancelFromSource`, `_cancelSameChain`, `onGetResponse`).

The Tron variant of the same contract has the identical unconditional-transfer pattern: [4](#0-3) 

There is no admin/governance recovery for stuck escrow — `SweepDust` only sweeps protocol-owned dust, not a specific order's escrowed inputs, and there is no mechanism to change an order's beneficiary or skip one problematic token while releasing the rest.

### Impact Explanation
Once a beneficiary (solver or user) becomes blocklisted on any single token that is part of an order's escrowed inputs or fees, that order's *entire* escrow (potentially multiple tokens, plus accrued relayer/tx fees) is permanently frozen inside the `IntentGatewayV2`/`ExtrinsicIntents`/`IntrinsicIntents` contract. Neither the user nor the solver has any means to recover the funds — `_withdraw` will revert every time it is invoked for that commitment, whether by relayer retry, cancellation, or refund flow. This is a permanent freezing of funds, satisfying the Medium/High severity bar (loss is a certainty, not merely a temporary delay, since the blocklisted address cannot be changed and there is no alternate beneficiary or force-skip mechanism).

### Likelihood Explanation
Triggering this does not require attacker privilege over the protocol: it only requires that a beneficiary address involved in escrow settlement ends up blocklisted by a widely-used stablecoin (USDC/USDT support blocklisting; it is exercised in production against sanctioned or compromised addresses). Since intent orders route arbitrary user- and solver-supplied addresses and tokens through `_withdraw`, and USDC is an explicitly expected settlement asset in the codebase's own tests, this is a realistic, if not frequent, occurrence — and once it occurs there is no mitigation.

### Recommendation
Make `_withdraw` resilient to a single failing transfer:
- Wrap each per-token transfer in a low-level call and, on failure, credit the amount to an internal pull-payment balance (`claimable[token][beneficiary] += amount`) instead of reverting the whole function, so other tokens/fees in the same order still settle.
- Provide a separate `claim(token)` function beneficiaries can call once unblocked, or that allows redirecting to an alternate address they control.
- Apply the same pattern to the Tron variant (`evm/tron/contracts/apps/IntentGatewayV2.sol`) and to the `HyperFungibleToken`/`WrappedHyperFungibleToken` mint/transfer-on-`onAccept` paths, which have the analogous single-recipient bottleneck.

### Proof of Concept
1. User places a cross-chain order with `inputs = [USDC(1000), DAI(500)]`, destination chain solver fills it.
2. Before the `RedeemEscrow` settlement message is delivered on the source chain, the solver's address is added to USDC's blocklist (e.g., due to unrelated sanctions/compliance action, or an attacker front-running an exploit report to get the address flagged).
3. Relayer delivers the `RedeemEscrow` POST request; `ExtrinsicIntents.onAccept` → `_withdraw` executes the loop: the USDC `safeTransfer(solver, 1000)` reverts because the solver is blocklisted.
4. The entire `_withdraw` call reverts, so **not only the USDC but also the 500 DAI never leaves escrow** and the accrued transaction fee is never paid out.
5. `EvmHost.dispatchIncoming` deletes the request receipt and permits retries indefinitely, but every retry invokes the same reverting `_withdraw`, so the DAI and fee remain permanently locked alongside the USDC, with no function in the contract able to redirect or release them to a different, unblocked address.

### Citations

**File:** evm/src/apps/intentsv2/IntentsBase.sol (L451-485)
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

        if (finalize) {
            uint256 fees = _orders[body.commitment][TRANSACTION_FEES];
            if (fees > 0) {
                delete _orders[body.commitment][TRANSACTION_FEES];
                IERC20(IDispatcher(host()).feeToken()).safeTransfer(beneficiary, fees);
            }

            if (isRefund) {
                emit EscrowRefunded({commitment: body.commitment, tokens: body.tokens});
            } else {
                emit EscrowReleased({commitment: body.commitment, tokens: body.tokens});
            }
        }
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

**File:** evm/src/core/EvmHost.sol (L811-818)
```text

        if (!success) {
            // so that it can be retried
            delete _requestReceipts[commitment];
            return;
        }
        emit PostRequestHandled({commitment: commitment, relayer: relayer});
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
