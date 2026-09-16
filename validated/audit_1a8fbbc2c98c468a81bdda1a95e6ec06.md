### Title
Tron `IntentGatewayV2.placeOrder` lacks the `nonReentrant` guard present in the canonical EVM implementation - (File: evm/tron/contracts/apps/IntentGatewayV2.sol)

### Summary
This is the same bug class as the reported `depositERC20To` missing `onlyEOA`: a function that has a documented, security-relevant modifier on its canonical sibling is missing that modifier on an alternate/ported implementation, weakening the guarantee users of the sibling function rely on.

### Finding Description
The canonical `IntentGatewayV2.placeOrder` in `evm/src/apps/IntentGatewayV2.sol` is declared as: [1](#0-0) 

with the `nonReentrant` modifier explicitly applied, guarding the escrow-transfer/predispatch-call logic that follows (which calls into an arbitrary `ICallDispatcher(dispatcher).dispatch(order.predispatch.call)` and transfers user tokens into escrow).

The Tron port of the same contract, `evm/tron/contracts/apps/IntentGatewayV2.sol`, declares the equivalent function as: [2](#0-1) 

with no `nonReentrant` modifier, and the contract itself does not inherit any `ReentrancyGuard`: [3](#0-2) 

The main EVM version's `placeOrder` executes `order.predispatch.call` via `ICallDispatcher(dispatcher).dispatch(...)` before finishing the escrow bookkeeping (fee-token swap via Uniswap V2, escrow snapshot/sweep), which is precisely the kind of external-call-before-effects pattern that motivated the reentrancy guard on the canonical contract and the CEI hardening documented for `_fillSameChain`/`_fillCrossChain` in `evm/src/apps/intentsv2/IntrinsicIntents.sol` and exercised in `evm/tests/foundry/IntrinsicIntentsReentrancyTest.sol`. The Tron port carries the identical `predispatch`-call/escrow-transfer logic but omits the corresponding reentrancy protection, exactly analogous to `depositERC20To` in the audit report inheriting the sensitive logic of `depositERC20` without the same protective modifier.

### Impact Explanation
If the Tron deployment's `placeOrder` is reentered (e.g. via a malicious `predispatch.call` target, or fee-on-transfer/callback token, or the Uniswap swap path) before nonce/commitment/escrow state is finalized, an attacker could manipulate escrow accounting — placing overlapping orders, duplicating nonces, or corrupting the fee-reduced input calculation used for the commitment hash — leading to permanent freezing or theft of escrowed user funds on the Tron deployment of the intents system.

### Likelihood Explanation
Likelihood depends on whether any external call reachable during `placeOrder` (predispatch dispatch, ERC20 `transferFrom` on a malicious/callback-capable token, or the Uniswap V2 swap for solver fees) can be triggered by an attacker-controlled contract before order state is finalized. Given the canonical EVM contract's authors explicitly added `nonReentrant` to this exact function and separately hardened `_fillSameChain`/`_fillCrossChain` against reentrancy (with dedicated regression tests), the codebase's own security posture treats this attack surface as real; its absence on the Tron variant is a direct regression of that protection.

### Recommendation
Add a `nonReentrant` modifier (or inherit `ReentrancyGuard` and apply it consistently) to `placeOrder`, `fillOrder`, and `cancelOrder` in `evm/tron/contracts/apps/IntentGatewayV2.sol`, matching the protections already present in `evm/src/apps/IntentGatewayV2.sol`, so the Tron deployment has the same reentrancy guarantees as the canonical EVM implementation.

### Proof of Concept
Not independently verified end-to-end (no reentrancy PoC contract exists yet for the Tron variant in the indexed test suite); the finding rests on direct comparison of modifier lists between the two `placeOrder` implementations:
- Canonical: `function placeOrder(Order memory order, bytes32 graffiti) public payable nonReentrant` [1](#0-0) 
- Tron: `function placeOrder(Order memory order, bytes32 graffiti) public payable {` (no `nonReentrant`) [2](#0-1)

### Citations

**File:** evm/src/apps/IntentGatewayV2.sol (L194-194)
```text
    function placeOrder(Order memory order, bytes32 graffiti) public payable nonReentrant {
```

**File:** evm/tron/contracts/apps/IntentGatewayV2.sol (L55-56)
```text
contract IntentGatewayV2 is HyperApp, EIP712 {
    using SafeERC20 for IERC20;
```

**File:** evm/tron/contracts/apps/IntentGatewayV2.sol (L338-338)
```text
    function placeOrder(Order memory order, bytes32 graffiti) public payable {
```
