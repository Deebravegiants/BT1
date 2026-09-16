## Title
Reentrancy in `IntentGatewayV2.withdraw()` (Tron variant) transfers escrowed tokens/fees before decrementing accounting state - ([File: evm/tron/contracts/apps/IntentGatewayV2.sol])

### Summary
The Tron-targeted `IntentGatewayV2` contract's internal `withdraw()` function performs external token/native transfers to a solver- or user-controlled `beneficiary` *before* updating the `_orders` escrow-accounting mapping, violating the Checks-Effects-Interactions pattern that the mainline EVM implementation (`evm/src/apps/intentsv2/IntentsBase.sol::_withdraw`) already enforces.

### Finding Description
In `evm/tron/contracts/apps/IntentGatewayV2.sol`, `withdraw()` loops over `body.tokens`, checks only that `_orders[body.commitment][token] != 0` (not the exact remaining balance), performs the transfer via a raw low-level `.call` (native ETH) or `token.call(transfer(...))` (ERC-20), and only afterwards decrements `_orders[body.commitment][token] -= amount`: [1](#0-0) 

The same after-the-fact bookkeeping pattern is repeated for transaction fees, where `IERC20(feeToken).call(transfer(...))` fires before `delete _orders[body.commitment][TRANSACTION_FEES]`: [2](#0-1) 

This is precisely the bug class the external report describes (transfer-then-deduct instead of deduct-then-transfer). By contrast, the mainline EVM `IntentsBase._withdraw` was hardened against this exact issue — it decrements `_orders[body.commitment][token]` *before* calling `_sendValue`/`safeTransfer`: [3](#0-2) 

and the project's own regression test suite documents that the equivalent CEI ordering bug in `_fillSameChain` was previously exploitable and had to be fixed by moving `_filled[commitment] = msg.sender` to the top of the function, before any external call: [4](#0-3) 

However, in the Tron `withdraw()`, `_filled[body.commitment] = beneficiary` is set at the top of the function (line 693), which does block re-entry into `fillOrder`/`cancelOrder` for the *same* commitment, but it does **not** protect the per-token escrow bookkeeping within the same `withdraw()` call. Because `body.tokens` originates directly from `order.inputs` (attacker-controlled at order-placement time, in `placeOrder`), an attacker can:
1. Include their own malicious ERC-20 (or a token with a transfer hook, e.g., ERC-777-style or a token with a `beforeTokenTransfer`/`tokensReceived` callback) as one of the order's input tokens when placing the order, alongside a second legitimate token.
2. Have that malicious token's `transfer()` implementation re-enter the gateway when it receives control during the withdraw loop, before `_orders[body.commitment][token] -= amount` runs for that token, and before the second, unrelated token's still-outstanding `_orders[commitment][token2]` balance is protected by anything beyond a non-zero check.
3. Re-enter `withdraw`-adjacent state readers (e.g. `cancelOrder`'s storage-proof path, or a subsequent legitimate `onAccept` delivery for a *different* commitment reusing the same escrow bookkeeping token address) — though the `onlyHost` modifier on `onAccept`/`onGetResponse` substantially narrows the direct external re-entrancy surface for a second `withdraw()` call in the same transaction context, since only the host can invoke it again.

### Impact Explanation
If a token with reentrant hooks (or a token itself controlled/upgradeable by the order's beneficiary) is escrowed as an order input, the transfer-before-decrement ordering means the escrow ledger (`_orders[commitment][token]`) is stale for the duration of the external call. Combined with the loose `== 0` check (rather than checking `escrowed >= amount`), this creates a window where accounting invariants used elsewhere (e.g., `cancelOrder`'s existence checks at lines 550-557, which only check `_orders[...] == 0`) can be manipulated to double-account or bypass "already withdrawn" checks, potentially leading to double payout of escrowed input tokens or protocol fees — a direct theft-of-funds / unbacked-transfer scenario from the intents escrow.

### Likelihood Explanation
Medium-to-High: exploitation requires the attacker (as order user) to supply a malicious/hooked token as an order input — something fully within an unprivileged user's control at `placeOrder` time — and requires the destination chain's fill/settlement flow to route that token through `withdraw()`. No privileged role is needed; a solver or a colluding user could set this up. The `onlyHost` gate on `onAccept`/`onGetResponse` limits the most direct re-entry into a second whole `withdraw()` invocation within the same call stack, which is a mitigating factor I could not fully rule out without deeper tracing of `EvmHost`'s delivery-then-callback ordering on Tron; this should be verified by a background engineer with test tooling.

### Recommendation
Apply the same CEI fix already present in `evm/src/apps/intentsv2/IntentsBase.sol` to the Tron `IntentGatewayV2.withdraw()`: decrement `_orders[body.commitment][token]` (and delete the `TRANSACTION_FEES` entry) *before* performing the external `.call`/`safeTransfer`, and replace the `== 0` existence check with an exact `escrowed >= amount` check (using `SafeERC20.safeTransfer` instead of raw low-level `.call` + manual success check, consistent with the mainline contract).

### Proof of Concept
Not independently executable from the index alone — reproducing requires deploying the Tron `IntentGatewayV2`, a malicious ERC-20 with a transfer hook as an order input, and driving `placeOrder` → cross-chain settlement → `onAccept`/`withdraw()`, similar to the `ReentrantBeneficiary` harness already present in the repo's mainline reentrancy tests: [5](#0-4) 
A background Devin session with Foundry access would be needed to build an equivalent PoC against the Tron variant and confirm exploitability given the `onlyHost` guard on `onAccept`.

### Citations

**File:** evm/tron/contracts/apps/IntentGatewayV2.sol (L696-714)
```text
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

**File:** evm/tron/contracts/apps/IntentGatewayV2.sol (L716-723)
```text
        // redeem tx fees
        uint256 fees = _orders[body.commitment][TRANSACTION_FEES];
        if (fees > 0) {
            address feeToken = IDispatcher(host()).feeToken();
            (bool success,) = feeToken.call(abi.encodeWithSelector(IERC20.transfer.selector, beneficiary, fees));
            if (!success) revert TransferFailed();
            delete _orders[body.commitment][TRANSACTION_FEES];
        }
```

**File:** evm/src/apps/intentsv2/IntentsBase.sol (L461-470)
```text
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

**File:** evm/tests/foundry/IntrinsicIntentsReentrancyTest.sol (L32-49)
```text
/**
 * @title ReentrantBeneficiary
 * @notice Malicious beneficiary contract that attempts to re-enter `fillOrder` during
 *         the ETH transfer made by `_fillSameChain` or `_fillCrossChain`.
 *
 * Attack window (pre-fix):
 *
 *   _fillSameChain / _fillCrossChain:
 *     beneficiary.call{value: ...}("")   ← RE-ENTRY HERE
 *     // _filled still == address(0) pre-fix, now set at the top (CEI)
 *
 * With the CEI fix in place, `_filled[commitment]` is set to `msg.sender` at the
 * very start of both fill functions. Any reentrant `fillOrder` call therefore hits
 * the `if (_filled[commitment] != address(0)) revert Filled()` guard and reverts.
 * That revert propagates through `receive()`, causing the outer ETH transfer to
 * return `(false, ...)`, which triggers `InsufficientNativeToken()` in the outer
 * call — rolling back all state changes atomically.
 */
```

**File:** evm/tests/foundry/IntrinsicIntentsReentrancyTest.sol (L50-83)
```text
contract ReentrantBeneficiary {
    IntentGatewayV2 public immutable gateway;

    Order private storedOrder;
    FillOptions private storedOptions;
    bool private armed;
    bool private reentered;

    constructor(address payable _gateway) {
        gateway = IntentGatewayV2(_gateway);
    }

    /// @notice Pre-approve the gateway to pull an ERC-20 from this contract.
    function approveGateway(address token, uint256 amount) external {
        IERC20(token).approve(address(gateway), amount);
    }

    /// @notice Load the reentrant payload before the outer fill is triggered.
    function arm(Order calldata order, FillOptions calldata options) external {
        storedOrder = order;
        storedOptions = options;
        armed = true;
    }

    /// @notice Triggered by the ETH transfer inside the fill loop.
    ///         Attempts to re-enter fillOrder; with the CEI fix the call reverts
    ///         with Filled(), which propagates and fails the outer ETH transfer.
    receive() external payable {
        if (armed && !reentered) {
            reentered = true;
            gateway.fillOrder(storedOrder, storedOptions);
        }
    }
}
```
