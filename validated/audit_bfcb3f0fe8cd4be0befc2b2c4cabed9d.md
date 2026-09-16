### Title
Cross-chain `RedeemEscrow`/`RefundEscrow` settlement hard-codes a fixed beneficiary address, so a restricted-transfer token (blacklist) permanently freezes the escrow with no recovery path - ([File: evm/src/apps/intentsv2/IntentsBase.sol])

### Summary
`IntentGatewayV2`'s cross-chain fill flow escrows a user's input tokens on the source chain and only releases them once a `RedeemEscrow` (or `RefundEscrow`) message is delivered back from the destination chain, naming a single, immutable beneficiary address baked into the message body at fill/cancel time. `_withdraw` in `IntentsBase.sol` performs a plain `safeTransfer(beneficiary, amount)` to that address with no fallback. If the beneficiary is an address the input token restricts transfers to/from (e.g. a Circle/Tether-style blacklist, a paused/sanctioned account, or any ERC-20 with transfer-gating logic), the transfer permanently reverts. Because the order is already marked filled/cancelled (`_filled[commitment]` is set) before this point, there is no way to re-target the release to a different beneficiary or to fall back to a refund — the escrowed tokens are stuck in the contract forever. This mirrors the reported EigenLayer issue: a withdrawal/settlement path assumes a fixed destination address can always receive the transfer, while an external token/protocol-level restriction can make that address permanently unable to receive funds, with no way to redirect or unwind the operation.

### Finding Description
- On the destination chain, `_fillCrossChain` (`evm/src/apps/intentsv2/ExtrinsicIntents.sol:164-220`) marks the order filled (`_filled[commitment] = msg.sender`) and dispatches a `RedeemEscrow` message whose beneficiary is hard-coded to `bytes32(uint256(uint160(msg.sender)))` — the filler's own address at fill time:
```solidity
_filled[commitment] = msg.sender;
...
_post(order, _body(RequestKind.RedeemEscrow, commitment, order.inputs,
    bytes32(uint256(uint160(msg.sender)))), options.relayerFee, nativeFee);
```
- On the source chain, `onAccept` decodes this `WithdrawalRequest` and calls `_withdraw` (`evm/src/apps/intentsv2/IntentsBase.sol:451-485`), which transfers escrowed ERC-20 tokens directly to that fixed beneficiary:
```solidity
function _withdraw(WithdrawalRequest memory body, bool isRefund, bool finalize) internal {
    address beneficiary = address(uint160(uint256(body.beneficiary)));
    if (finalize) _filled[body.commitment] = beneficiary;
    ...
    IERC20(token).safeTransfer(beneficiary, amount);
```
- The same pattern exists for `RefundEscrow` (cancel path) and in the Tron variant (`evm/tron/contracts/apps/IntentGatewayV2.sol:691-730`, using a low-level `token.call(transfer(...))` that reverts with `TransferFailed()`).
- If the beneficiary address is subject to a transfer-level restriction on the escrowed token (blacklist, freeze, sanctions list — common on stablecoins like USDC/USDT, which are explicitly used as intent-gateway input tokens in the test suite), `safeTransfer`/the low-level `transfer` call reverts every time this message is delivered.
- `EvmHost.dispatchIncoming` swallows a reverting `onAccept` and deletes the receipt so the message "stays deliverable" (per `sdk/packages/core/docs/ai/flows/how-a-cross-chain-delivery-reaches-the-gateway-and-where-the.md`), meaning the message can be resubmitted indefinitely but will always fail against the same immutable beneficiary — there is no way to change the beneficiary because it is embedded in the already-computed, already-dispatched message body.
- Because `_filled[commitment]` was already set on the destination chain before dispatch, `cancelOrder` (`evm/src/apps/IntentGatewayV2.sol:505-537`) reverts with `Filled()` for this commitment, so the user has no alternate path to reclaim the escrowed input tokens either. The escrow is permanently locked in the source-chain gateway contract.

### Impact Explanation
This is a concrete, permanent freezing-of-funds bug reachable by any ordinary user/solver interaction with the Intent Gateway (no privileged role required): a user places a cross-chain order, a solver fills it, and the settlement message that should release the user's escrowed tokens is delivered to a fixed address that the token itself refuses to credit. The escrowed input tokens become permanently unrecoverable — not merely delayed — since (a) the beneficiary is fixed and cannot be changed, (b) the message keeps being retried and keeps reverting, and (c) the order's "filled" state blocks the normal cancel/refund route. This satisfies the "permanent freezing of funds" acceptance criterion for the intents escrow bug class.

### Likelihood Explanation
The trigger condition — a beneficiary address becoming unable to receive a specific ERC-20 due to an issuer-level restriction — is realistic for exactly the kind of tokens the Intent Gateway is built to move (USDC/USDT and similar tokens are used as escrowed inputs in the test suite, e.g. `evm/tests/foundry/IntentGatewayV2Test.sol`). No attacker collusion, governance compromise, or privileged access is required: a solver's own address (or a same-chain refund recipient) merely needs to end up on a blacklist/freeze list at any point before the settlement message is finally delivered, which can happen for reasons entirely outside the protocol's control (e.g., regulatory action, contract flagged by an exchange/issuer). Given multi-block/cross-chain settlement latency, the window in which this can occur is non-trivial.

### Recommendation
Do not tie fund release to an unconditional, hard-coded `transfer`/`safeTransfer` to a single immutable address embedded at fill time. Instead:
1. Wrap the token transfer in `_withdraw` (and its Tron equivalent) in a try/catch (or low-level call check) that, on failure, credits an internal "claimable balance" for the intended beneficiary rather than reverting/looping forever.
2. Provide a separate, permissionless `claim()`/`redirectClaim(newBeneficiary)` function that lets the intended beneficiary (or, after a timeout, the original order creator) pull the credited balance to an alternate address they control, so a single restricted address cannot permanently lock the funds.
3. Ensure the "already filled" state does not by itself preclude every recovery path — e.g., allow a beneficiary-redirect governance/relayer path or a timeout-based sweep once a transfer has failed a bounded number of times.

### Proof of Concept
1. User places a cross-chain order on chain A, escrowing 10,000 USDC as input (`IntentGatewayV2.placeOrder`).
2. A solver fills the order on chain B (`fillOrder` → `_fillCrossChain`), delivering the required output tokens to the user and dispatching `RedeemEscrow` with `beneficiary = solver`. `_filled[commitment]` is now set on chain B.
3. Before the `RedeemEscrow` message is delivered/settled on chain A, the solver's address is added to USDC's `isBlacklisted` list (e.g., by Circle, for an unrelated reason).
4. A relayer submits the `RedeemEscrow` proof to chain A; `onAccept` → `_withdraw` calls `IERC20(usdc).safeTransfer(solver, 10000e6)`, which reverts because the recipient is blacklisted.
5. `EvmHost.dispatchIncoming` swallows the revert and clears the receipt, so the message can be resubmitted — but every resubmission fails identically because `beneficiary` is fixed inside the already-signed/dispatched message body.
6. The user cannot call `cancelOrder` on chain A because `_filled[commitment] != address(0)` (set in step 2 on chain B, mirrored via the message), so `Filled()` is reverted.
7. The 10,000 USDC escrowed on chain A is now permanently stuck in the `IntentGatewayV2` contract with no code path to release it to anyone. [1](#0-0) [2](#0-1) [3](#0-2) [4](#0-3) [5](#0-4)

### Citations

**File:** evm/src/apps/intentsv2/ExtrinsicIntents.sol (L164-220)
```text
    function _fillCrossChain(Order calldata order, FillOptions calldata options, bytes32 commitment) internal {
        uint256 outputsLen = order.output.assets.length;

        _filled[commitment] = msg.sender;

        uint256 msgValue = msg.value;
        address beneficiary = address(uint160(uint256(order.output.beneficiary)));
        TokenInfo[] memory outputFills = new TokenInfo[](outputsLen);

        for (uint256 i; i < outputsLen; i++) {
            bytes32 outputToken = order.output.assets[i].token;
            if (options.outputs[i].token != outputToken) revert InvalidInput();

            address token = address(uint160(uint256(outputToken)));
            uint256 totalRequired = order.output.assets[i].amount;
            uint256 solverAmount = options.outputs[i].amount;

            if (solverAmount < totalRequired) revert InvalidInput();

            (uint256 protocolShare, uint256 beneficiaryShare) =
                _splitSurplus(solverAmount - totalRequired, order.output.call.length > 0);

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
    }
```

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

**File:** evm/src/apps/IntentGatewayV2.sol (L505-537)
```text
    function cancelOrder(Order calldata order, CancelOptions calldata options) public payable nonReentrant {
        bytes32 commitment = keccak256(abi.encode(order));

        if (_filled[commitment] != address(0)) revert Filled();

        address hostAddr = host();
        bytes32 currentChain = keccak256(IDispatcher(hostAddr).host());
        bytes32 orderSource = keccak256(order.source);
        bytes32 orderDest = keccak256(order.destination);
        bool isSameChain = orderSource == orderDest;

        // Emitted here, once, rather than from each of the three routes below. Every check those
        // routes make — Unauthorized, NotExpired, UnknownOrder — reverts, and a revert discards
        // logs, so an early emit can never announce a cancellation that did not happen. Emitting
        // before the branch also keeps `EscrowRefunded` the last log on the same-chain route, where
        // the refund is processed in this same transaction. Three emit sites cost bytecode this
        // contract does not have: it sits within ~100 bytes of the EIP-170 limit.
        emit OrderCancelled({commitment: commitment, canceller: msg.sender});

        if (isSameChain) {
            // Checked here rather than inside `_cancelSameChain`, which used to re-read `host()`,
            // re-query the host's state machine id and re-hash `order.source` to reach the same
            // answer this function already has. Same check, one external call fewer.
            if (currentChain != orderSource) revert WrongChain();
            _cancelSameChain(order, commitment);
        } else if (currentChain == orderSource) {
            _cancelFromSource(order, options, commitment);
        } else if (currentChain == orderDest) {
            _cancelFromDest(order, options, commitment);
        } else {
            revert WrongChain();
        }
    }
```

**File:** evm/tron/contracts/apps/IntentGatewayV2.sol (L691-730)
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

        if (isRefund) {
            emit EscrowRefunded({commitment: body.commitment});
        } else {
            emit EscrowReleased({commitment: body.commitment});
        }
    }
```

**File:** sdk/packages/core/docs/ai/flows/how-a-cross-chain-delivery-reaches-the-gateway-and-where-the.md (L10-13)
```markdown
2. `EvmHost.dispatchIncoming` (restricted to the handler) writes a receipt for the request
   commitment, then low-level calls the module with `IApp.onAccept(IncomingPostRequest(request,
   relayer))`. If that call fails the host deletes the receipt and returns without reverting, so the
   rest of the batch proceeds and the message stays deliverable.
```
