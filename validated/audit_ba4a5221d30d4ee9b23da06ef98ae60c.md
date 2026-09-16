### Title
`_withdraw` bundles fee-token distribution with escrow release, letting one recipient-specific ERC20 revert permanently freeze unrelated escrowed funds - (File: evm/src/apps/intentsv2/IntentsBase.sol)

### Summary
`IntentsBase._withdraw` is the single internal function that releases escrowed order tokens to a beneficiary. When `finalize` is true it also forwards any accumulated protocol fee (in the fixed protocol `feeToken`, e.g. USDC/USDT) to that same beneficiary, in the same atomic call, with no isolation between the two transfers. [1](#0-0) 

### Finding Description
`_withdraw` first loops over the order's escrowed input/output tokens and transfers them to `beneficiary`, then — only when `finalize` is true — transfers any accrued `TRANSACTION_FEES` in the protocol `feeToken` to that *same* beneficiary via `IERC20(IDispatcher(host()).feeToken()).safeTransfer(beneficiary, fees)`. [2](#0-1) 

Because this is a single Solidity call, a revert anywhere inside — including the unrelated fee-token transfer — unwinds the entire function, including the transfers of the principal escrowed assets that had already "succeeded" earlier in the same call. `feeToken` is a single, protocol-wide, governance-settable ERC-20 (see `IDispatcher.feeToken()` / `EvmHost.feeToken`), and is realistically a centralized stablecoin such as USDC or USDT, both of which support recipient blacklisting/freezing at the token contract level. If the `beneficiary` address (the order user for `RefundEscrow`/same-chain-cancel, or the filler/solver for `RedeemEscrow`) is ever blacklisted by that stablecoin issuer for any reason unrelated to Hyperbridge, `IERC20(feeToken).safeTransfer(beneficiary, fees)` reverts every time it is attempted.

This function is reached from every path that finalizes an order:
- Cross-chain `onAccept` for `RedeemEscrow`/`RefundEscrow`, driven by any relayer delivering a Hyperbridge message. [3](#0-2) 
- `onGetResponse` for source-chain cancellation. [4](#0-3) 
- Same-chain cancel, callable directly and unprivileged by `order.user`. [5](#0-4) 
- Same-chain fill finalize path. [6](#0-5) 

None of these callers retry with the fee-forwarding step skipped, and there is no separate "claim escrow only" entry point — `_withdraw` always attempts the fee transfer whenever `_orders[commitment][TRANSACTION_FEES] > 0`, and it is the only function that clears escrow accounting (`_orders[...][token] -= amount`) and releases the principal tokens. There is no way to retry the message with the fee omitted, and no alternate code path to release the principal escrow independent of the fee sweep.

This is structurally the same defect as the referenced JPEG'd finding: a generic, must-succeed operation (`Controller.setStrategy` calling `strategy.withdraw()`) is coupled to a token-specific code path that the underlying asset can unconditionally reject (JPEG being blacklisted in `withdraw()`), permanently bricking the generic operation. Here, the generic operation is "release a user's/solver's escrow," and the token-specific code path that can unconditionally reject is the protocol `feeToken` transfer to the same beneficiary.

### Impact Explanation
Any escrowed input or output tokens belonging to an order with `order.fees > 0` become permanently unrecoverable the moment the beneficiary address is blacklisted by the `feeToken` issuer (a real-world, non-Hyperbridge event entirely outside the protocol's control, e.g. USDC/USDT compliance actions). Because escrow release and cancellation both route through `_withdraw`, neither a legitimate fill settlement nor a cancellation/refund can ever succeed for that beneficiary — the order's principal assets are frozen in the gateway contract indefinitely, with no governance override or alternate withdrawal path exposed by the contract. This is a permanent freezing-of-funds condition reachable without any admin or relayer misbehavior — it requires only a normal fee-bearing order plus an external, entirely foreseeable event on the fee stablecoin.

### Likelihood Explanation
Every order that sets `order.fees > 0` (the common case, since fee-bearing orders are the expected/normal usage documented for the fill fee) is exposed. The triggering condition — the beneficiary being blacklisted by the fee-token issuer — is outside the control of Hyperbridge, the order's creator, or the solver, and stablecoin blacklisting of individual addresses is a documented, occasionally-exercised capability of USDC/USDT. Given the wide range of participants (any user placing an order, any solver filling one) and the long lifetime of pending/escrowed orders, the probability that at least one beneficiary becomes blacklisted over the life of the protocol is non-trivial, and the resulting freeze is total and irreversible for that order.

### Recommendation
Decouple fee-token distribution from principal escrow release so a failure in one cannot block the other:
- Wrap the fee-token transfer in `_withdraw` so a revert there does not unwind the principal transfers (e.g., use a low-level `call` with a `try/catch`-style pattern instead of `safeTransfer`, and on failure route the fee to a recoverable, separately-swept balance rather than reverting the whole function), mirroring `SweepDust`'s pattern of tolerating per-token transfer outcomes independently.
- Alternatively, perform the fee-token transfer and the principal-token transfers as fully independent operations/messages so `_withdraw`'s core escrow release cannot be gated on the fee transfer's success.

### Proof of Concept
1. Governance sets `feeToken` to a blacklistable stablecoin such as USDC or USDT via `_updateParams`.
2. A user places a cross-chain order with `order.fees > 0` and `order.user = U`; the fee is escrowed under `_orders[commitment][TRANSACTION_FEES]`. [7](#0-6) 
3. Before the order is filled/cancelled, the stablecoin issuer blacklists address `U` for reasons unrelated to Hyperbridge.
4. `U` (or any relayer, for the cross-chain cancel/refund path) attempts to cancel/refund via `cancelOrder` → `_cancelFromSource`/`_cancelFromDest` → `onGetResponse`/`onAccept` → `_withdraw(body, true, true)`.
5. Inside `_withdraw`, the principal input tokens are transferred to `U` successfully, but the subsequent `IERC20(feeToken).safeTransfer(U, fees)` reverts because `U` is blacklisted by the token contract. [8](#0-7) 
6. The whole transaction reverts, so `_orders[commitment][token]` is never decremented and the principal tokens are never actually delivered — the escrow remains locked in the gateway with no way to retry `_withdraw` successfully, since `U`'s blacklist status cannot be changed by the protocol.

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

**File:** evm/src/apps/intentsv2/ExtrinsicIntents.sol (L360-366)
```text
    function onGetResponse(IncomingGetResponse calldata incoming) external override onlyHost {
        _checkRelayer(incoming.relayer);
        if (incoming.response.values[0].value.length != 0) revert Filled();

        WithdrawalRequest memory body = abi.decode(incoming.response.request.context, (WithdrawalRequest));
        _withdraw(body, true, true);
    }
```

**File:** evm/src/apps/intentsv2/IntrinsicIntents.sol (L121-129)
```text
        // Orders carrying output calldata must be filled completely in a single fill.
        // The attached call is only executed on a full fill, so a partial fill would
        // leave the intended side effect unexecuted while releasing proportional escrow.
        if (order.output.call.length > 0 && !isFullyFilled) revert PartialFillNotAllowed();

        WithdrawalRequest memory body = WithdrawalRequest({
            commitment: commitment, tokens: escrowedInputs, beneficiary: bytes32(uint256(uint160(msg.sender)))
        });
        _withdraw(body, false, isFullyFilled);
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

**File:** evm/src/apps/IntentGatewayV2.sol (L375-392)
```text
        if (order.fees > 0) {
            address feeToken = IDispatcher(hostAddr).feeToken();
            if (msgValue > 0) {
                address uniswapV2 = IDispatcher(hostAddr).uniswapV2Router();
                address WETH = IUniswapV2Router02(uniswapV2).WETH();
                address[] memory path = new address[](2);
                path[0] = WETH;
                path[1] = feeToken;
                uint256[] memory amounts = IUniswapV2Router02(uniswapV2).swapETHForExactTokens{value: msgValue}(
                    order.fees, path, address(this), block.timestamp
                );
                msgValue -= amounts[0];
            } else {
                IERC20(feeToken).safeTransferFrom(msg.sender, address(this), order.fees);
            }

            _orders[commitment][TRANSACTION_FEES] = order.fees;
        }
```
