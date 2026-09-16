### Title
Reentrancy in `IntentGatewayV2.withdraw` (Tron) — external token/native transfer precedes escrow-balance decrement - ([File: evm/tron/contracts/apps/IntentGatewayV2.sol])

### Summary
The Tron variant of `IntentGatewayV2` implements a `withdraw` function that violates checks-effects-interactions: it performs the external ETH/token transfer to the beneficiary *before* decrementing the corresponding `_orders[commitment][token]` escrow balance, unlike the hardened `IntentsBase._withdraw` (EVM) which was already patched with a CEI fix (confirmed by `IntrinsicIntentsReentrancyTest.sol`). This mirrors the Coral incident's reentrancy class, where an external call executed prior to state finalization let an attacker re-enter and drain escrowed funds.

### Finding Description
In `evm/tron/contracts/apps/IntentGatewayV2.sol`, `withdraw()` is invoked from `onAccept()` for `RedeemEscrow`/`RefundEscrow` message kinds and from `onGetResponse()` for cancellation settlements: [1](#0-0) 

The loop iterates escrowed tokens and, for each, sends the ETH/token to `beneficiary` via a low-level `.call` **before** updating `_orders[body.commitment][token]`: [2](#0-1) 

If `beneficiary` is a contract (native ETH branch) or implements ERC-777/ERC-1363-style hooks (token branch), it can re-enter during the external call. Because `_orders[body.commitment][token]` for tokens later in the same `body.tokens` array has *not yet* been decremented, and because the fee-release block (`_orders[body.commitment][TRANSACTION_FEES]`) also transfers before/independent of consistent state at that point, a malicious beneficiary contract can potentially re-invoke a reachable external entry point (e.g. another `withdraw`-triggering incoming message processed by the same relayer flow, or any function reading `_orders[commitment][...]` for a not-yet-decremented token) to double-spend the remaining escrow for that commitment, mirroring the wRAM double-drain in the Coral incident.

This directly contrasts with the fixed EVM path (`evm/src/apps/intentsv2/IntentsBase.sol::_withdraw`), which decrements `_orders[commitment][token]` **before** the external transfer: [3](#0-2) 

The Tron contract lacks this ordering and has no reentrancy guard on `withdraw`, `onAccept`, or `onGetResponse`.

### Impact Explanation
A successful reentrant call during the beneficiary transfer in a multi-token withdrawal could allow draining escrowed input tokens or protocol/transaction fees beyond what is legitimately owed for a commitment, resulting in direct theft of bridged/escrowed funds on the Tron deployment of Hyperbridge's IntentGateway — a concrete loss of user/solver funds analogous to the Coral wRAM reentrancy drain. This qualifies as Medium/High severity theft of escrowed funds.

### Likelihood Explanation
Likelihood is Medium: exploitation requires the attacker to control the `beneficiary` address of an order (which the order-placing user or a colluding party freely controls in `PaymentInfo.beneficiary`/`body.beneficiary`) and for the order to escrow multiple tokens (or native ETH plus a fee token) so a reentrant window exists before all balances are zeroed. The pattern is a well-known, directly reachable reentrancy from an ordinary user-controlled beneficiary address, requiring no privileged role — consistent with the unprivileged relayer/settlement path this analysis is scoped to.

### Recommendation
Apply the same CEI fix already present in `IntentsBase._withdraw` to the Tron `IntentGatewayV2.withdraw`: decrement `_orders[body.commitment][token]` (and delete `_orders[body.commitment][TRANSACTION_FEES]`) *before* performing any external `.call` transfer of ETH/tokens to `beneficiary`. Additionally consider adding a reentrancy guard (`nonReentrant`) to `onAccept`/`onGetResponse` as defense in depth.

### Proof of Concept
1. Attacker places (or is designated beneficiary of) a cross-chain order whose settlement triggers `withdraw()` with `body.tokens` containing both native ETH (`token == address(0)`) and an ERC-20 (or a fee-token release) for the same `commitment`.
2. A relayer submits the settlement proof; `onAccept` calls `withdraw(body, ...)`.
3. In the loop, the first entry (`token == address(0)`) sends ETH via `beneficiary.call{value: amount}("")` *before* `_orders[body.commitment][address(0)] -= amount` executes.
4. The malicious `beneficiary` contract's `receive()` re-enters a reachable external function that reads/acts on `_orders[body.commitment][ERC20_token]` (still showing the pre-decrement, fully-escrowed balance) or re-triggers the fee-transfer block, extracting funds beyond the intended single settlement.
5. Because no reentrancy guard exists on this call path, and the escrow ledger only zeroes out after the external call returns, the attacker can obtain more value than escrowed for that commitment before the top-level `withdraw` call completes its bookkeeping. [4](#0-3)

### Citations

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
