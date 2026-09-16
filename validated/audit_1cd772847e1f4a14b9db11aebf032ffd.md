### Title
Predispatch sweep in `placeOrder` credits an order with any pre-existing balance held by the shared `CallDispatcher`, not funds actually contributed by the caller - (File: `evm/src/apps/IntentGatewayV2.sol`)

### Summary
`IntentGatewayV2.placeOrder` has a predispatch path that, like the reported `_transferTokens` bug, substitutes a balance check on a shared contract for a verified transfer from the caller. Instead of crediting an order's escrowed input with exactly what the caller moved in, it sweeps the *entire* current balance of the target token/ETH held by the shared `CallDispatcher` into the gateway and treats it as the order's input.

### Finding Description
In the predispatch branch of `placeOrder`, the caller supplies `order.predispatch.assets` (pushed into the `dispatcher`) and `order.predispatch.call` (arbitrary calldata executed by the dispatcher). After executing that call, the code does not verify how much of the *actual* required input token the predispatch call produced from the caller's own assets — it instead reads the dispatcher's raw balance and sweeps all of it: [1](#0-0) 

Specifically:
- For native token inputs: `balance = address(dispatcher).balance; if (balance < requiredAmount) revert; transferCalls[i] = Call({to: address(this), value: balance, data: ""})` — sweeps the dispatcher's *whole* ETH balance, not just what this caller's predispatch call generated. [2](#0-1) 
- For ERC20 inputs: identical pattern using `IERC20(token).balanceOf(dispatcher)`. [3](#0-2) 

The subsequent "received" accounting only measures the delta on the **gateway's** own balance (`address(this).balance` / `balanceOf(address(this))`) before/after the sweep, and any excess over `requiredAmount` is emitted as `DustCollected` and simply attributed to the *current* order rather than reverted or returned to whoever actually left it there: [4](#0-3) 

Because `order.predispatch.call` is attacker-controlled arbitrary calldata executed by the shared `dispatcher`, an attacker can submit a `predispatch.call` that does nothing meaningful for the required input token (or one unrelated token) while depositing a trivial `predispatch.assets` amount (the only requirement is `assets.length > 0`), and still have the sweep step pull in and credit whatever balance of the target input token/ETH is *already sitting* in `dispatcher` — regardless of whether it came from this caller's contribution. This mirrors the audited `_transferTokens` flaw: relying on a contract's ambient balance instead of an authenticated transfer tied to the sender, letting an unprivileged caller siphon value that isn't theirs.

### Impact Explanation
If the shared `CallDispatcher` ever holds a residual balance of a token/ETH (e.g., leftover dust from a previous order's predispatch swap that wasn't fully enumerated in that order's `inputs`, or any token accidentally/intentionally sent to it), any subsequent unrelated caller can place an order that "escrows" that balance as their own input by supplying a minimal/no-op predispatch call and dummy assets. Since the escrowed input backs a promised payout to a solver/filler on the destination chain (via `_orders[commitment][token] += ...`), this allows an attacker to redeem cross-chain fills using funds they never actually deposited — a direct theft-of-funds vector reachable from a single `placeOrder` transaction by any unprivileged intent submitter.

### Likelihood Explanation
Requires the `CallDispatcher` to hold a nonzero balance of the target token/native asset at the time of the attacker's `placeOrder` call. This is plausible in production because: the dispatcher is a shared, generically-callable execution surface used across multiple flows (predispatch swaps, HFT/WrappedHFT calldata execution), so stray balances (fee-on-transfer remainders, rounding excess from swaps, previously "dust"-flagged amounts) can realistically accumulate there over time and be reachable to any single submitted order.

### Recommendation
Do not infer the caller's contribution from the dispatcher's raw balance. Snapshot the dispatcher's balance for each relevant token *before* pushing `predispatch.assets` and executing `predispatch.call`, and only sweep the balance *increase* attributable to this specific call (`balanceAfter - balanceBefore`), reverting if that delta is less than `requiredAmount`. This ties the escrowed input strictly to funds this caller actually introduced in this transaction, eliminating the ability to claim ambient/residual dispatcher balances.

### Proof of Concept
1. Assume the shared `CallDispatcher` currently holds `100 USDC` (e.g., left over from a prior order whose predispatch call generated excess USDC not listed in that order's `inputs`).
2. Attacker calls `placeOrder` with:
   - `order.predispatch.assets = [{token: DUST_TOKEN, amount: 1}]` (trivial, unrelated token, just to satisfy `assets.length > 0`)
   - `order.predispatch.call` = a no-op/self-call that does not move any real value for USDC
   - `order.inputs = [{token: USDC, amount: 100e6}]`
3. In `placeOrder`, per [3](#0-2) , `balance = IERC20(USDC).balanceOf(dispatcher)` returns the pre-existing `100 USDC`, which satisfies `balance >= requiredAmount`, and the full balance is swept to the gateway via `transferCalls[i]`.
4. The attacker's order is now escrowed with `100 USDC` input that the attacker never transferred, entitling them to the promised destination-chain payout once a solver fills the order — a theft of the dispatcher's ambient balance.

### Citations

**File:** evm/src/apps/IntentGatewayV2.sol (L263-287)
```text
            for (uint256 i; i < inputsLen;) {
                if (order.inputs[i].amount == 0) revert InvalidInput();
                address token = address(uint160(uint256(order.inputs[i].token)));
                uint256 requiredAmount = order.inputs[i].amount;

                if (token == address(0)) {
                    uint256 balance = address(dispatcher).balance;
                    if (balance < requiredAmount) revert InsufficientNativeToken();
                    transferCalls[i] = Call({to: address(this), value: balance, data: ""});
                    balancesBefore[i] = address(this).balance;
                } else {
                    uint256 balance = IERC20(token).balanceOf(dispatcher);
                    if (balance < requiredAmount) revert InvalidInput();
                    transferCalls[i] = Call({
                        to: token,
                        value: 0,
                        data: abi.encodeWithSelector(IERC20.transfer.selector, address(this), balance)
                    });
                    balancesBefore[i] = IERC20(token).balanceOf(address(this));
                }

                unchecked {
                    ++i;
                }
            }
```

**File:** evm/src/apps/IntentGatewayV2.sol (L291-311)
```text
            // Measure actual received, emit dust for excess, update order.inputs.
            for (uint256 i; i < inputsLen;) {
                address token = address(uint160(uint256(order.inputs[i].token)));
                uint256 received;
                if (token == address(0)) {
                    received = address(this).balance - balancesBefore[i];
                } else {
                    received = IERC20(token).balanceOf(address(this)) - balancesBefore[i];
                }

                if (received > order.inputs[i].amount) {
                    uint256 dust = received - order.inputs[i].amount;
                    emit DustCollected(token, dust);
                } else {
                    order.inputs[i].amount = received;
                }

                unchecked {
                    ++i;
                }
            }
```
