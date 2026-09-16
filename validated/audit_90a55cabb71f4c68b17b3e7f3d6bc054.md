### Title
Interactions-before-effects in `IntentGatewayV2.withdraw()` (Tron variant) — escrow decrement occurs after external token/ETH transfer - (File: `evm/tron/contracts/apps/IntentGatewayV2.sol`)

### Summary
The Tron-specific `IntentGatewayV2` reimplementation violates the Checks-Effects-Interactions pattern in `withdraw()`: for every escrowed asset it performs the external transfer call (native ETH `.call` or ERC20 `.call(transfer)`) *before* decrementing `_orders[body.commitment][token]`, and likewise transfers the transaction fee before deleting `_orders[body.commitment][TRANSACTION_FEES]`. This is the exact bug class in the referenced mai-protocol `Collateral.sol` audit finding, and it is a regression relative to the main EVM `IntentsBase._withdraw` (`evm/src/apps/intentsv2/IntentsBase.sol`), which was hardened with CEI (escrow debited before transfer) after an equivalent finding, as documented by the dedicated `IntrinsicIntentsReentrancyTest.sol` regression suite.

### Finding Description
`withdraw()` in `evm/tron/contracts/apps/IntentGatewayV2.sol` (lines 691-730): [1](#0-0) 

sets `_filled[body.commitment] = beneficiary` first (CEI-compliant for that variable), but for each token in the loop it does:
```
if (_orders[body.commitment][token] == 0) revert UnknownOrder();
// external call/transfer happens here
_orders[body.commitment][token] -= amount;   // effect happens AFTER interaction
```
and for fees:
```
(bool success,) = feeToken.call(...transfer...);
delete _orders[body.commitment][TRANSACTION_FEES];  // effect after interaction
```
Unlike the main EVM implementation's `IntentsBase._withdraw`, which decrements escrow (`_orders[body.commitment][token] = escrowed - amount;`) *before* the transfer: [2](#0-1) 

the Tron variant keeps the interaction-before-effect ordering. `withdraw()` is reachable from: `onAccept` (RedeemEscrow/RefundEscrow, gated `onlyHost`), `onGetResponse` (gated `onlyHost`), and directly from the unprivileged, user-callable `cancelOrder()` same-chain branch: [3](#0-2) 

Because `_orders[commitment][token]` is checked only against `!= 0` (not `>= amount`) and remains at its stale (pre-decrement) value for the duration of every external call in the loop, any escrowed asset whose transfer can trigger a callback (native ETH sent to a contract beneficiary, or an ERC20/ERC777-style token with transfer hooks — both of which are fully attacker-selectable at `placeOrder()` time since `order.inputs[i].token` and `order.output.beneficiary` are supplied by the order creator) executes with the ledger not yet updated to reflect the payout in progress.

### Impact Explanation
Although reentry into `withdraw()` itself for the *same* commitment is blocked by the early `_filled[commitment]` write (paralleling the fix validated for the main EVM contract by `IntrinsicIntentsReentrancyTest.sol`), the CEI violation on `_orders[...][token]` still means that, for the duration of each iteration's external call, the escrow ledger for that specific token/fee entry has not yet been decremented. This is a structural violation of the safe-withdrawal pattern the codebase has already had to fix once (the EVM `IntentsBase` history plus the dedicated reentrancy test suite prove the project explicitly treats this ordering as security-critical). Any function added in the future that reads `_orders[commitment][token]` (or any code path invoked mid-loop across other tokens in the same `body.tokens` array, or fee accounting) inherits a window where escrowed value appears available even though a transfer for it is in flight, directly matching the Medium-severity classification of the referenced audit finding — the risk is state/event ordering corruption and, given the stale mapping value during the callback window, a foothold for double-payout if any additional entry point (present or introduced) trusts `_orders[commitment][token] != 0` as proof of un-spent escrow.

### Likelihood Explanation
Reachable from a fully unprivileged path: any user calling `cancelOrder()` for a same-chain order they created, or any relayer delivering a legitimate `RedeemEscrow`/`RefundEscrow` message, triggers `withdraw()`. The attacker fully controls the escrowed token contract and the beneficiary address at order-placement time, so triggering a callback during the transfer is trivial. The only mitigating factor is the `_filled` guard blocking a full re-entrant re-execution of `withdraw()` for the identical commitment through the currently-known call paths (`cancelOrder`, `onAccept`, `onGetResponse`), which lowers immediate exploitability to a "trust-boundary/defense-in-depth failure" rather than a demonstrated fund-drain in the current, single-entry-point codebase — hence Medium rather than High/Critical.

### Recommendation
Apply the same fix already used in `IntentsBase._withdraw` (`evm/src/apps/intentsv2/IntentsBase.sol` lines 461-469) to the Tron contract: decrement `_orders[body.commitment][token]` (and `delete`/zero the fee entry) *before* performing the native/ERC20 transfer in `withdraw()`, so effects are fully committed prior to any external interaction, consistent with Checks-Effects-Interactions and with the precedent already set — and tested — elsewhere in this codebase.

### Proof of Concept
1. Create a same-chain `Order` where `order.inputs` includes a token contract the attacker controls that implements a transfer hook (or use native ETH with `order.output.beneficiary`/`order.user` set to an attacker-controlled contract).
2. Call `placeOrder()`, escrowing the malicious asset; `_orders[commitment][maliciousToken] = amount`.
3. Call `cancelOrder()` as the order owner for the same-chain branch, which invokes `withdraw(body, true)`.
4. Inside `withdraw()`, at line 706 (`token.call(...transfer...)`) the malicious token's hook fires while `_orders[commitment][maliciousToken]` is still equal to `amount` (not yet decremented at line 710) — demonstrating the interaction-before-effect window described above; any future code path (or currently-unaudited entry) reading this mapping mid-callback would observe stale, over-stated escrow. [4](#0-3)

### Citations

**File:** evm/tron/contracts/apps/IntentGatewayV2.sol (L516-539)
```text
    function cancelOrder(Order calldata order, CancelOptions calldata options) public payable {
        bytes32 commitment = keccak256(abi.encode(order));

        // order has already been filled
        if (_filled[commitment] != address(0)) revert Filled();

        address hostAddr = host();
        bytes32 currentChain = keccak256(IDispatcher(hostAddr).host());
        bytes32 orderSource = keccak256(order.source);
        bytes32 orderDest = keccak256(order.destination);
        bool isSameChain = orderSource == orderDest;

        if (isSameChain) {
            // Same-chain: validate locally and refund immediately
            // only owner can cancel
            if (order.user != bytes32(uint256(uint160(msg.sender)))) revert Unauthorized();

            // Verify we're on the correct chain
            if (orderSource != currentChain) revert WrongChain();

            WithdrawalRequest memory body =
                WithdrawalRequest({commitment: commitment, tokens: order.inputs, beneficiary: order.user});

            withdraw(body, true);
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

**File:** evm/src/apps/intentsv2/IntentsBase.sol (L461-469)
```text
            uint256 escrowed = _orders[body.commitment][token];
            if (escrowed == 0) revert UnknownOrder();

            _orders[body.commitment][token] = escrowed - amount;
            if (token == address(0)) {
                _sendValue(beneficiary, amount);
            } else {
                IERC20(token).safeTransfer(beneficiary, amount);
            }
```
