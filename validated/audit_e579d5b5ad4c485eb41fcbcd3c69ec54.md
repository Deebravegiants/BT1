### Title
`IntentGatewayV2.placeOrder()` balance-diff accounting is reentrancy-exploitable on Tron (no reentrancy guard) - ([File: evm/tron/contracts/apps/IntentGatewayV2.sol])

### Summary
The Tron port of `IntentGatewayV2` computes the escrowed input amount for an order by diffing the gateway's/dispatcher's token balance before and after `safeTransferFrom`/sweep, exactly the same pattern flagged in the external report for `TokenFlow.moveOut()`. Unlike the main EVM contract, the Tron contract `IntentGatewayV2 is HyperApp, EIP712` has **no reentrancy guard at all**, so if a callback-capable token (e.g. TRC-777-style token with hooks, or any token with a hook to an arbitrary contract during `transferFrom`) is accepted as an order input, an attacker can reenter `placeOrder` during the transfer callback to make the balance-diff overcount tokens actually received, inflating on-chain escrow relative to tokens truly custodied.

### Finding Description
In `evm/src/apps/IntentGatewayV2.sol` `placeOrder()` (lines 291–329, corresponding logic mirrored at `evm/tron/contracts/apps/IntentGatewayV2.sol:421-469`), the actual amount escrowed for fee-on-transfer support is computed as:

```solidity
uint256 balBefore = IERC20(token).balanceOf(address(this));
IERC20(token).safeTransferFrom(msg.sender, address(this), order.inputs[i].amount);
order.inputs[i].amount = IERC20(token).balanceOf(address(this)) - balBefore;
``` [1](#0-0) 

and the sweep-based predispatch path similarly measures `received = balanceOf(address(this)) - balancesBefore[i]` after triggering a call dispatcher sweep: [2](#0-1) 

This is the identical accounting pattern the external report describes for `TokenFlow.moveOut()` — deriving a "received" amount purely from a balance delta around an external call, which is unsafe for any token that grants callbacks during transfer (hooks to sender/receiver), because a reentrant call during the transfer can move additional tokens into the contract or manipulate escrow bookkeeping in the callback window before the outer diff is taken, letting an attacker claim credit for more tokens than they actually locked in that specific call.

The primary EVM contract mitigates this at the contract level with `ReentrancyGuardTransient`: [3](#0-2) [4](#0-3) 

but the Tron variant, which contains the same balance-before/balance-after escrow logic in its `placeOrder()` (predispatch/sweep path at `evm/tron/contracts/apps/IntentGatewayV2.sol:421-469`), declares no such protection: [5](#0-4) 

No `nonReentrant` modifier or `ReentrancyGuard`/`ReentrancyGuardTransient` import exists anywhere in that file (confirmed by search returning zero matches), whereas the mainline EVM contract explicitly imports and inherits `ReentrancyGuardTransient` for this exact reason.

### Impact Explanation
If a callback-capable ("evil") token is listed as an order input asset on the Tron deployment, an attacker can craft a reentrant call during `transferFrom`/sweep to record a larger `received`/escrowed amount in `_orders[commitment][token]` than tokens actually transferred into the gateway. This inflates the commitment/escrow with unbacked value: a solver later filling that order and withdrawing escrow could extract more tokens than were ever deposited, draining the gateway's other users' funds — a direct fund-theft / insolvency vector reachable by any unprivileged order-placer, matching the "Medium/High" scope criteria (concrete theft/permanent freezing of funds via unsound accounting in a token-bridge/intents contract).

### Likelihood Explanation
Likelihood depends on whether a callback-token (e.g., a token with transfer hooks) is ever permitted as an order input asset on the Tron IntentGateway. Because `placeOrder` on Tron is a fully permissionless, unprivileged entry point (any user submits an `Order` naming arbitrary ERC-20 token addresses as inputs), and Tron's TRC-20 ecosystem includes tokens with custom transfer hooks/hidden logic, an attacker only needs to get such a token accepted (or deploy their own malicious token and target another order/dust-sweep path using that token) to trigger the flaw — no admin or governance action is required to reach the vulnerable code path itself, though token allow-listing (if any exists off-chain/at the gateway integration layer) would gate real-world exploitability.

### Recommendation
Add `ReentrancyGuardTransient` (or a standard `ReentrancyGuard`, since Tron's TVM may not support `TSTORE`/transient storage the same way) to `evm/tron/contracts/apps/IntentGatewayV2.sol` and apply a `nonReentrant` modifier to `placeOrder`, `fillOrder`, and any other function performing balance-diff accounting around external token calls, mirroring the protection already present in `evm/src/apps/IntentGatewayV2.sol`. Alternatively/additionally, explicitly document and enforce (via allow-listing) that only tokens without external transfer callbacks are supported as order input assets.

### Proof of Concept
1. Deploy a malicious TRC-20 token whose `transferFrom` calls back into `msg.sender` (attacker contract) before completing balance updates, similar to an ERC-777-style hook.
2. Attacker calls `placeOrder()` on the Tron `IntentGatewayV2` with this token as an input asset and a modest `amount`.
3. Inside the token's `transferFrom` callback, the attacker's contract reenters `placeOrder()` (or a related sweep path) again, before the outer call's `balanceOf` diff is taken, causing the outer transaction to observe an inflated `balanceOf(address(this))` when it finally computes `received = balanceOf(this) - balBefore`.
4. The resulting `order.inputs[i].amount` (escrowed amount) recorded in `_orders[commitment][token]` exceeds what the attacker actually transferred to the gateway in that top-level call.
5. Attacker (or accomplice acting as solver) fills the order and withdraws the inflated escrow, extracting more tokens than were deposited, at the expense of other users' pooled token balances in the gateway.

Note: I could not fully trace the Tron contract's dust-sweep / escrow-write code path beyond the excerpt at lines 421-469 within the indexing limits available; a full manual review of `evm/tron/contracts/apps/IntentGatewayV2.sol`'s complete `placeOrder`/`fillOrder`/withdrawal logic is recommended to confirm the exact exploitable state transition and quantify the maximum extractable amount.

### Citations

**File:** evm/src/apps/IntentGatewayV2.sol (L24-24)
```text
import {ReentrancyGuardTransient} from "@openzeppelin/contracts/utils/ReentrancyGuardTransient.sol";
```

**File:** evm/src/apps/IntentGatewayV2.sol (L60-60)
```text
contract IntentGatewayV2 is IntrinsicIntents, ExtrinsicIntents, ReentrancyGuardTransient, Initializable {
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

**File:** evm/src/apps/IntentGatewayV2.sol (L312-323)
```text
        } else {
            for (uint256 i; i < inputsLen;) {
                if (order.inputs[i].amount == 0) revert InvalidInput();
                address token = address(uint160(uint256(order.inputs[i].token)));
                if (token == address(0)) {
                    if (msgValue < order.inputs[i].amount) revert InsufficientNativeToken();
                    msgValue -= order.inputs[i].amount;
                } else {
                    uint256 balBefore = IERC20(token).balanceOf(address(this));
                    IERC20(token).safeTransferFrom(msg.sender, address(this), order.inputs[i].amount);
                    order.inputs[i].amount = IERC20(token).balanceOf(address(this)) - balBefore;
                }
```

**File:** evm/tron/contracts/apps/IntentGatewayV2.sol (L55-56)
```text
contract IntentGatewayV2 is HyperApp, EIP712 {
    using SafeERC20 for IERC20;
```
