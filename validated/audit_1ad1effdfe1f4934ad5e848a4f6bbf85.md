### Title
Unverified token address in `withdraw()` allows silent no-op transfers via raw low-level `.call` - (File: `evm/tron/contracts/apps/IntentGatewayV2.sol`)

### Summary
The Tron variant of `IntentGatewayV2.withdraw()` escrow-release path performs ERC20 transfers with a raw, unguarded `address.call(abi.encodeWithSelector(IERC20.transfer.selector, ...))` instead of using the hardened `SafeERC20` library used everywhere else in the same contract. Because a low-level `.call` to an address with no code always returns `success = true`, and the code here doesn't even check the returned `data` (unlike the classic `safeTransfer` pattern), any `token` address supplied by the order-placer that is not an actual ERC20 contract will make `withdraw()` "succeed" without moving any value.

### Finding Description
`order.inputs[i].token` and `order.output.assets[i].token` are fully attacker/user-controlled `bytes32` values, cast directly to `address` with no validation that the address is an actual token contract (no `code.length` check anywhere in the order-placement/escrow flow) [1](#0-0) .

In `withdraw()`, the escrow-release loop transfers escrowed tokens to the beneficiary using a bare low-level call rather than `SafeERC20.safeTransfer`: [2](#0-1) 

and the same pattern is used again for fee-token redemption: [3](#0-2) 

This is precisely the bug class from the referenced report: a low-level `.call()` against an address with no deployed bytecode (an EOA, or an attacker-chosen non-token contract) always returns `success = true` with empty `returndata`, since there's no code to execute or revert. The code only checks `success`, so it treats these as successful transfers even though nothing was transferred. Contrast this with the rest of the contract, which correctly `using SafeERC20 for IERC20` and calls `safeTransferFrom`/`safeTransfer` for escrow deposits [4](#0-3)  — OpenZeppelin's `SafeERC20` internally guards against exactly this by checking `address(token).code.length > 0` when `returndata` is empty, but that guard is bypassed here because `withdraw()` uses a raw `.call` instead of the library.

Because `_orders[commitment][token]` bookkeeping and escrow accounting never distinguish "real, contract-backed token" from "arbitrary attacker-chosen address," a solver/relayer filling and later withdrawing an order cannot detect, purely from the withdraw() success flag, whether the promised input tokens for a non-standard `token` address were ever actually escrowed or paid out.

### Impact Explanation
This breaks a core invariant of the intents escrow: that a "successful" `withdraw()` call implies tokens were actually delivered to the beneficiary. An order or withdrawal request referencing a bogus `token` address (EOA or contract with no code, or one that self-destructed) will report success on-chain while transferring zero value, silently desynchronizing the on-chain escrow ledger from actual token balances and letting a malicious order-placer construct commitments/withdrawal flows that appear fully settled without any real asset movement — directly matching the "no funds actually transferred, downstream logic treats it as settled" impact called out in the source report.

### Likelihood Explanation
`withdraw()` is reached from `onGetResponse` (host-gated) as part of the normal cross-chain intents refund flow, and the `token` values it iterates over trace back to attacker-controlled `Order`/`WithdrawalRequest` fields created in `placeOrder`, with no contract-code check anywhere in the pipeline. Any user submitting an order can pick an arbitrary `token` address, making this trivially reachable by an unprivileged relayer/order-placer/solver interacting with the intents flow, not requiring any privileged role.

### Recommendation
Replace the raw `token.call(abi.encodeWithSelector(IERC20.transfer.selector, ...))` calls in `withdraw()` with `IERC20(token).safeTransfer(beneficiary, amount)` (already imported and used elsewhere in this file via `using SafeERC20 for IERC20`), so the code-length/return-data guard OpenZeppelin's `SafeERC20` provides is applied consistently across every token transfer path in the contract.

### Proof of Concept
1. Attacker calls `placeOrder` with `order.inputs[0].token` set to an EOA address (or any address with no bytecode) and a nonzero `amount`.
2. During escrow, `_orders[commitment][token]` is credited with the reduced amount as usual (accounting only, no contract-existence check).
3. Order is filled/settled and eventually routed to `withdraw()` (e.g. via `onGetResponse` refund path).
4. In the token-redemption loop, `token.call(abi.encodeWithSelector(IERC20.transfer.selector, beneficiary, amount))` is issued against the code-less address; the EVM returns `success = true` with empty `returndata` because there is no code to execute.
5. `withdraw()` proceeds as if the transfer succeeded, decrementing `_orders[body.commitment][token] -= amount` and emitting `EscrowReleased`/`EscrowRefunded`, even though no value was ever moved to `beneficiary`.

### Citations

**File:** evm/tron/contracts/apps/IntentGatewayV2.sol (L55-56)
```text
contract IntentGatewayV2 is HyperApp, EIP712 {
    using SafeERC20 for IERC20;
```

**File:** evm/tron/contracts/apps/IntentGatewayV2.sol (L365-365)
```text
                address token = address(uint160(uint256(order.inputs[i].token)));
```

**File:** evm/tron/contracts/apps/IntentGatewayV2.sol (L705-708)
```text
            } else {
                (bool success,) = token.call(abi.encodeWithSelector(IERC20.transfer.selector, beneficiary, amount));
                if (!success) revert TransferFailed();
            }
```

**File:** evm/tron/contracts/apps/IntentGatewayV2.sol (L719-722)
```text
            address feeToken = IDispatcher(host()).feeToken();
            (bool success,) = feeToken.call(abi.encodeWithSelector(IERC20.transfer.selector, beneficiary, fees));
            if (!success) revert TransferFailed();
            delete _orders[body.commitment][TRANSACTION_FEES];
```
