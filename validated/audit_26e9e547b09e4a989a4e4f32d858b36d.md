I have enough evidence to confirm this vulnerability. The Tron variant of `IntentGatewayV2.sol` uses raw low-level `.call` with the ERC20 `transfer` selector and only checks the outer call-success boolean, never decoding/validating the returned ERC20 boolean — the exact bug class from the report, while the sibling EVM contracts (`evm/src/apps/intentsv2/IntentsBase.sol`, `HyperFungibleToken.sol`, etc.) correctly use OpenZeppelin's `SafeERC20.safeTransfer`.

### Title
Unchecked ERC20 boolean return value in `IntentGatewayV2` (Tron) escrow withdrawal/dust-sweep lets non-reverting tokens silently fail while state is finalized - (File: evm/tron/contracts/apps/IntentGatewayV2.sol)

### Summary
The Tron deployment of `IntentGatewayV2` releases escrowed order/fee tokens using a raw low-level `.call(abi.encodeWithSelector(IERC20.transfer.selector, ...))` and only checks that the external call itself did not revert, never validating the ERC20 `bool` return value. This is exactly the "unchecked transfer result" bug class: for ERC20 tokens that return `false` on failure instead of reverting, the low-level call succeeds (`success == true`) even though no tokens were transferred, yet the escrow accounting is unconditionally decremented/finalized.

### Finding Description
In `withdraw()`: [1](#0-0) 
each escrowed token is released via:
```solidity
(bool success,) = token.call(abi.encodeWithSelector(IERC20.transfer.selector, beneficiary, amount));
if (!success) revert TransferFailed();
_orders[body.commitment][token] -= amount;
```
and the same pattern is used for transaction fees and for `SweepDust`: [2](#0-1) 

`success` here only reflects whether the low-level call reverted, not whether `transfer()` returned `true`. Per EIP-20, tokens are permitted to return `false` on failure rather than reverting. For any such token accepted as an order's input/output asset (`order.inputs`/`order.output.assets` are attacker/user-supplied `TokenInfo.token` addresses), a `transfer` call that returns `false` will pass this check, `_orders[commitment][token] -= amount` will still execute, and `_filled[body.commitment]` will be set — permanently marking the order filled/refunded without the beneficiary ever receiving funds.

This directly mirrors the reported `FootiumPrizeDistributor` pattern where `transfer()`'s return value is ignored, except here it manifests as raw `.call` result-checking instead of a direct `IERC20.transfer()` call — same root cause (no `SafeERC20`/return-data decoding). Notably, this file imports `SafeERC20` and uses `safeTransferFrom` elsewhere in the same contract (e.g. `IERC20(token).safeTransferFrom(msg.sender, dispatcher, amount)` at lines 405/459/484), showing this specific `withdraw`/`SweepDust` path is an inconsistent, unsafe deviation from the rest of the codebase's convention (compare with `evm/src/apps/intentsv2/IntentsBase.sol` which correctly uses `IERC20(token).safeTransfer(beneficiary, amount)` at lines 468/476).

### Impact Explanation
The beneficiary (solver/filler or user refund recipient) permanently loses the escrowed funds: the commitment is marked filled/refunded and the escrow balance is decremented even though the token transfer silently failed. Because `_orders[commitment][token]` is decremented and `_filled[commitment]` set, there is no retry path — the funds become stuck/unrecoverable in the contract for any token whose `transfer` can return `false` without reverting, satisfying "permanent freezing of funds" for that escrow.

### Likelihood Explanation
`IntentGatewayV2` is explicitly designed to be compatible with arbitrary ERC20 tokens supplied as order inputs/outputs by users/solvers (`address token = address(uint160(uint256(order.inputs[i].token)))`), so any order or fill route in Tron's Intents flow that uses a non-reverting ERC20 (a class of tokens that does exist, and is a known edge case explicitly called out for compatibility in this exact bug class) will trigger fund loss on every withdrawal through this path.

### Recommendation
Replace the raw `.call` + `success`-only check with OpenZeppelin's `SafeERC20.safeTransfer` (already imported and used elsewhere in this file), which decodes and validates the ERC20 return value (and handles tokens with no return value) for the three affected sites: the `SweepDust` transfer, the per-token escrow release, and the transaction-fee release in `withdraw()`.

### Proof of Concept
1. An order specifies `order.inputs[i].token` = a maliciously/non-standard ERC20 contract whose `transfer(address,uint256)` returns `false` on some condition (e.g., insufficient allowance-like internal check) instead of reverting.
2. The order is filled and later `withdraw()` is invoked (via `onGetResponse`/redeem-escrow request handling) to release the escrowed token to the beneficiary.
3. `token.call(abi.encodeWithSelector(IERC20.transfer.selector, beneficiary, amount))` returns `(success=true, data=abi.encode(false))` — the call itself doesn't revert.
4. The code only checks `success`, so it proceeds: `_orders[body.commitment][token] -= amount;` and `_filled[body.commitment] = beneficiary;` are executed.
5. The beneficiary receives zero tokens, yet the order is now marked filled and the escrow accounting shows the funds as disbursed — the tokens remain permanently locked in the `IntentGatewayV2` contract with no code path to reclaim them. [3](#0-2)

### Citations

**File:** evm/tron/contracts/apps/IntentGatewayV2.sol (L661-682)
```text
        } else if (kind == RequestKind.SweepDust) {
            SweepDust memory req = abi.decode(incoming.request.body[1:], (SweepDust));

            uint256 outputsLen = req.outputs.length;
            for (uint256 i; i < outputsLen;) {
                TokenInfo memory info = req.outputs[i];
                address token = address(uint160(uint256(info.token)));
                uint256 amount = info.amount;

                if (token == address(0)) {
                    (bool sent,) = req.beneficiary.call{value: amount}("");
                    if (!sent) revert InsufficientNativeToken();
                } else {
                    (bool success,) = token.call(abi.encodeWithSelector(IERC20.transfer.selector, req.beneficiary, amount));
                    if (!success) revert TransferFailed();
                }
                unchecked {
                    ++i;
                }
                emit DustSwept(token, amount, req.beneficiary);
            }
        }
```

**File:** evm/tron/contracts/apps/IntentGatewayV2.sol (L691-722)
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
```
