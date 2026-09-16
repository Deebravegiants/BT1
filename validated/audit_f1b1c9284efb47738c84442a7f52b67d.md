### Title
Reentrancy in the Tron IntentGatewayV2's escrow release/withdraw path via pre-decrement external calls and missing reentrancy guards - (File: evm/tron/contracts/apps/IntentGatewayV2.sol)

### Summary
The Tron variant of the Intent Gateway (`evm/tron/contracts/apps/IntentGatewayV2.sol`) diverges from the hardened, reentrancy-guarded EVM mainline `evm/src/apps/IntentGatewayV2.sol`. Its `withdraw()` function pays out escrowed native/ERC-20 tokens to an attacker-controllable `beneficiary` address via a raw external `.call` *before* decrementing the corresponding `_orders[commitment][token]` escrow balance, and none of the contract's externally reachable entry points (`placeOrder`, `fillOrder`, `cancelOrder`, `onAccept`, `onGetResponse`) carry a `nonReentrant` guard — unlike the mainline contract, which applies `nonReentrant` to `placeOrder`/`fillOrder` and sets `_filled`/decrements escrow before any external transfer in `IntentsBase._withdraw`.

### Finding Description
`withdraw()` in the Tron gateway: [1](#0-0) 

iterates escrowed tokens for a commitment and, per token, executes a low-level `.call` to `beneficiary` (native ETH) or to the token contract (`transfer`) **before** updating `_orders[body.commitment][token] -= amount`. This is a checks-effects-interactions violation: the external call happens while the escrow ledger for that token still reflects the pre-payout balance. The equivalent function in the mainline contract, `IntentsBase._withdraw`, decrements `_orders` (the "effect") strictly before the `_sendValue`/`safeTransfer` (the "interaction"): [2](#0-1) 

Additionally, the mainline `placeOrder`/`fillOrder` are explicitly `nonReentrant`: [3](#0-2) 

while the Tron `placeOrder` carries no such modifier: [4](#0-3) 

The reachable actor here is exactly the "intent solver / filler" role in scope: a solver that both places an order (as `order.user`) and fills it as its own solver becomes the `beneficiary` of the `RedeemEscrow`/`RefundEscrow` payout that triggers `withdraw()`. If that beneficiary is a smart contract, its `receive()`/token callback executes attacker-controlled logic mid-loop, with the escrow ledger for the just-paid token not yet decremented and no reentrancy lock anywhere in the contract to stop a nested call into the gateway's other unprotected external functions (`placeOrder`, `cancelOrder`, `select`).

### Impact Explanation
This is a fund-safety-relevant CEI violation in a contract that directly custodies escrowed user/solver funds (native ETH and ERC-20 tokens). Because no `nonReentrant` guard exists anywhere in this file, and the state that other code paths rely on (`_orders[commitment][token]`) is stale during the external call, this significantly weakens the invariant that escrow accounting and payouts are atomic — mirroring the "state updated after minting/external call" pattern described in the reference report (H-04), which enabled multi-minting/manipulation via reentrant calls before state finalized. The blast radius is the escrow pool for the specific IntentGateway deployment (all commingled orders' escrowed tokens), so unbacked payouts here constitute direct fund loss.

### Likelihood Explanation
Medium-High reachability: an attacker only needs to (a) act as both the order placer and the solver/filler of their own order (both permissionless, unprivileged roles explicitly in scope — "intent solver, bandwidth purchaser" analog), and (b) use a smart-contract beneficiary address that reenters on receiving the native-ETH leg of a multi-token withdrawal. No relayer or governance privilege is required to reach `withdraw()` — it fires automatically once the (attacker's own) settlement message is delivered by any relayer through the standard `onAccept`/`onGetResponse` path. The missing `nonReentrant` modifiers mean this is a genuine, currently-open gap in this file, in contrast to the explicitly tested and CEI-fixed mainline `IntrinsicIntents`/`ExtrinsicIntents` fill logic (see `IntrinsicIntentsReentrancyTest.sol`), which shows the project is otherwise aware of and defends against exactly this bug class elsewhere.

### Recommendation
- Apply the same Checks-Effects-Interactions ordering used in `IntentsBase._withdraw`: decrement `_orders[commitment][token]` before performing the native/ERC-20 transfer in the Tron `withdraw()`.
- Add `nonReentrant` (OpenZeppelin `ReentrancyGuard`) to all externally reachable state-changing functions in `evm/tron/contracts/apps/IntentGatewayV2.sol` (`placeOrder`, `fillOrder`, `cancelOrder`, `onAccept`, `onGetResponse`), matching the guard already present on `evm/src/apps/IntentGatewayV2.sol`.
- Use `SafeERC20.safeTransfer` instead of raw `.call(abi.encodeWithSelector(...))` for token payouts, consistent with the mainline contract.

### Proof of Concept
1. Attacker deploys a malicious `beneficiary` contract with a `receive()` that calls back into the Tron `IntentGatewayV2` (e.g., `placeOrder` or another unguarded entry point) the first time it receives ETH.
2. Attacker (as `order.user`) places a same-chain-style order whose inputs escrow both native ETH and an ERC-20 token, then also acts as the solver/filler on the destination side so that the `RedeemEscrow`/`RefundEscrow` message names the malicious contract as `beneficiary`.
3. A relayer (can be the attacker) delivers the settlement message; `onAccept` calls `withdraw()`.
4. In the loop, the native-ETH branch executes `beneficiary.call{value: amount}("")` for the first token entry, before `_orders[body.commitment][token] -= amount` runs for that entry.
5. The malicious contract's `receive()` reenters the gateway; since no `nonReentrant` guard exists anywhere in the contract, the reentrant call is not blocked at the contract level (unlike the mainline gateway, which reverts on any reentrant `fillOrder`/`placeOrder`), demonstrating the missing protection documented as fixed elsewhere in the codebase (`IntrinsicIntentsReentrancyTest.sol`) but absent here. [5](#0-4)

### Citations

**File:** evm/tron/contracts/apps/IntentGatewayV2.sol (L338-338)
```text
    function placeOrder(Order memory order, bytes32 graffiti) public payable {
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

**File:** evm/src/apps/IntentGatewayV2.sol (L194-194)
```text
    function placeOrder(Order memory order, bytes32 graffiti) public payable nonReentrant {
```
