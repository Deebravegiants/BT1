### Title
`IntentGatewayV2.placeOrder` (Tron variant) permanently locks excess native token overpayment instead of refunding it - (File: evm/tron/contracts/apps/IntentGatewayV2.sol)

### Summary
The Tron-specific `IntentGatewayV2.placeOrder` function accepts `msg.value` and consumes it for native-token order inputs and, optionally, for a Uniswap swap to pay `order.fees`, but — unlike the canonical EVM implementation — it never returns any unspent remainder of `msg.value` to the caller. Any ETH/TRX sent beyond what is strictly required is permanently stranded in the contract with no accounting entry and no recovery path, directly matching the reported bug class of "amount sent does not reconcile with `msg.value`."

### Finding Description
`placeOrder` decodes `order.inputs` and `order.predispatch.assets` and, for each entry with `token == address(0)`, deducts the required amount from a local `msgValue` counter while validating `msgValue >= amount` (reverting with `InsufficientNativeToken` if not) [1](#0-0) . If `order.fees > 0`, any remaining `msgValue` is swapped via `swapETHForExactTokens` for an exact amount of fee token, but the actual native amount consumed by the swap (`amounts[0]`) is never subtracted from `msgValue`, nor is any leftover value refunded afterward [2](#0-1) .

The function then proceeds directly to emitting `OrderPlaced` and returns [3](#0-2) . There is no line comparable to the canonical (non-Tron) `IntentGatewayV2.sol`'s explicit refund step:
```
// Refund any unspent native tokens to the user.
if (msgValue > 0) {
    _sendValue(msg.sender, msgValue);
}
```
which exists in `evm/src/apps/IntentGatewayV2.sol` [4](#0-3)  but is absent from the Tron fork of the same contract.

Consequently, any `msg.value` sent to `placeOrder` on Tron that exceeds the sum of native input amounts plus the exact native amount consumed by the fee-swap (or the sum of native inputs, when `order.fees == 0` and there is no swap) is silently absorbed by the contract balance, with no escrow entry (`_orders[commitment][...]`) crediting it to the user and no other function in the contract exposing a way to reclaim it — `cancelOrder`/`withdraw` only operate on amounts already recorded in `_orders`, which excludes this unaccounted leftover [5](#0-4) .

### Impact Explanation
This is a direct, permanent loss of user funds reachable by any unprivileged caller through a single `placeOrder` transaction — the exact bug class described in the source report (function consumes `msg.value` without reconciling it against the sum of amounts actually used, causing depositor losses when `msg.value` exceeds the required sum). Because the surplus is never tracked in `_orders`, it cannot be recovered even via order cancellation, making the loss permanent. Given the ease of triggering it (any user overestimating `nativeFee`/`nativeValue` when constructing the transaction, or the Uniswap swap consuming less than the full remaining `msgValue`), this qualifies as High severity permanent freezing/loss of user funds.

### Likelihood Explanation
Likelihood is high: the SDK-documented placement flow explicitly instructs users to add `nativeValue` (a fee quote) to `value` before signing (`docs/content/developers/evm/intent-gateway/placing-orders.mdx`), and any imprecision between the quoted `nativeValue` and the actual Uniswap swap execution price (slippage, price movement between quoting and execution) will leave a nonzero remainder that is silently kept. Ordinary usage patterns (rounding up native transfer amounts, quoting fees slightly conservatively) will trigger this on essentially every order that pays fees in native token, or whenever a user accidentally overpays for native-token inputs.

### Recommendation
Add the same unspent-value refund logic present in the canonical `evm/src/apps/IntentGatewayV2.sol` to the Tron variant: after the fee-swap branch, subtract the actual amount consumed by `swapETHForExactTokens` (its first return value) from `msgValue`, and refund any remaining `msgValue` to `msg.sender` (e.g., via a low-level `call{value: msgValue}("")` with success check, matching the pattern in `_sendValue`) before emitting `OrderPlaced`.

### Proof of Concept
1. User calls `placeOrder{value: X}(order, graffiti)` on the Tron `IntentGatewayV2` with an order containing only ERC-20 inputs (or native inputs summing to `Y < X`) and `order.fees > 0`.
2. `msgValue` starts at `X`; native inputs (if any) deduct `Y`, leaving `X - Y`.
3. The fee branch executes `swapETHForExactTokens{value: X - Y}(order.fees, ...)`, which only consumes the exact native amount needed to produce `order.fees` of fee token (call it `Z <= X - Y`); Uniswap refunds the router's own leftover to `msg.sender = address(this)` per its semantics — but in this code, `msgValue` (the accounting variable) is never decremented by `Z`, and no refund of the true remainder `(X - Y - Z)` reaching the contract is issued.
4. The transaction completes successfully, `OrderPlaced` is emitted, and `(X - Y - Z)` wei of native token permanently remains in the `IntentGatewayV2` contract balance, uncredited in `_orders` and unrecoverable by the user via `cancelOrder` or any other public function.

### Citations

**File:** evm/tron/contracts/apps/IntentGatewayV2.sol (L450-461)
```text
        } else {
            for (uint256 i; i < inputsLen;) {
                if (order.inputs[i].amount == 0) revert InvalidInput();
                address token = address(uint160(uint256(order.inputs[i].token)));
                if (token == address(0)) {
                    // native token
                    if (msgValue < order.inputs[i].amount) revert InsufficientNativeToken();
                    msgValue -= order.inputs[i].amount;
                } else {
                    IERC20(token).safeTransferFrom(msg.sender, address(this), order.inputs[i].amount);
                }

```

**File:** evm/tron/contracts/apps/IntentGatewayV2.sol (L471-488)
```text
        if (order.fees > 0) {
            // escrow fees
            address feeToken = IDispatcher(hostAddr).feeToken();
            if (msgValue > 0) {
                address uniswapV2 = IDispatcher(hostAddr).uniswapV2Router();
                address WETH = IUniswapV2Router02(uniswapV2).WETH();
                address[] memory path = new address[](2);
                path[0] = WETH;
                path[1] = IDispatcher(hostAddr).feeToken();
                IUniswapV2Router02(uniswapV2).swapETHForExactTokens{value: msgValue}(
                    order.fees, path, address(this), block.timestamp
                );
            } else {
                IERC20(feeToken).safeTransferFrom(msg.sender, address(this), order.fees);
            }

            _orders[commitment][TRANSACTION_FEES] = order.fees;
        }
```

**File:** evm/tron/contracts/apps/IntentGatewayV2.sol (L490-506)
```text
        emit OrderPlaced({
            user: order.user,
            source: order.source,
            destination: order.destination,
            deadline: order.deadline,
            nonce: order.nonce,
            fees: order.fees,
            session: order.session,
            predispatch: order.predispatch.assets,
            inputs: reducedInputs,
            beneficiary: order.output.beneficiary,
            outputs: order.output.assets,
            predispatchCall: order.predispatch.call,
            outputCall: order.output.call,
            graffiti: graffiti
        });
    }
```

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

**File:** evm/src/apps/IntentGatewayV2.sol (L394-397)
```text
        // Refund any unspent native tokens to the user.
        if (msgValue > 0) {
            _sendValue(msg.sender, msgValue);
        }
```
