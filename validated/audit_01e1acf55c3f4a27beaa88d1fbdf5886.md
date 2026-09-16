### Title
Unchecked ERC20 `transfer` return value in `withdraw()`/`onAccept` SweepDust path allows silent-failure token loss and stuck escrow - (File: evm/tron/contracts/apps/IntentGatewayV2.sol)

### Summary
The Tron variant of `IntentGatewayV2` uses raw low-level `.call()` to invoke `IERC20.transfer` when releasing escrowed intent funds and sweeping dust, checking only that the call did not revert (`success`) but never decoding/validating the boolean return value of `transfer`. Non-reverting, non-standard ERC20 tokens that return `false` on failure will be treated as successful transfers, permanently corrupting escrow accounting and freezing/losing user funds — the same unsafe-transfer bug class as the referenced UXD report.

### Finding Description
In `withdraw()`, called from `onAccept` (RedeemEscrow/RefundEscrow) and from `onGetResponse`, escrowed order tokens are released to the beneficiary via: [1](#0-0) 

The code only checks `success` from the raw `.call`, which is `true` as long as the call does not revert — it does not decode the ABI-encoded boolean returned by `transfer()`. Any ERC-20 implementation that returns `false` instead of reverting on failure (a well-known non-standard-but-legal behavior, e.g. some tokens under low balance/blacklist conditions) will pass this check even though no tokens were actually moved. Immediately after, `_orders[body.commitment][token] -= amount;` decrements the escrow bookkeeping as if the transfer succeeded, so the beneficiary can never retry or reclaim the funds — the escrow entry is deleted/decremented but the token balance never left the contract.

The same unsafe pattern also appears in the `SweepDust` admin action within `onAccept`: [2](#0-1) 
and for the transaction-fee redemption: [3](#0-2) 

`withdraw()` is reachable from a relayed/verified ISMP message (`onAccept` guarded by `onlyHost` and `authenticate(incoming.request)` for RedeemEscrow/RefundEscrow) and from `onGetResponse` (verified GET response for refund-on-timeout), i.e. it fires whenever a relayer delivers a proven cross-chain fill/refund message — a standard, unprivileged relaying path in the intents flow: [4](#0-3) [5](#0-4) 

By contrast, the primary EVM `IntentGatewayV2` inbound/outbound transfer paths use `SafeERC20.safeTransferFrom`/import `SafeERC20`: [6](#0-5) 
and other order-placement code paths in the same file correctly use `safeTransferFrom`: [7](#0-6) 
but the escrow-release (`withdraw`) and dust-sweep code paths were left using the unchecked raw `.call` + selector pattern instead of `SafeERC20.safeTransfer`, creating an inconsistency and the vulnerability.

### Impact Explanation
If a whitelisted collateral/intent token silently returns `false` on transfer failure (rather than reverting), a user who is entitled to redeem escrowed input tokens (order filler, refund recipient, or dust sweep beneficiary) will receive nothing while the contract's internal accounting (`_orders[commitment][token]`) is decremented/deleted as though the transfer succeeded. This results in a permanent loss/freezing of user/protocol funds trapped in the `IntentGatewayV2` contract with no recovery path, since the escrow state no longer reflects an outstanding balance. This matches the "permanent freezing of funds" / "concrete theft" acceptance criteria.

### Likelihood Explanation
Likelihood depends on whether a non-reverting-on-failure ERC20 token is ever escrowed as an intent input/output asset on the Tron intents deployment. Given that intent gateways are explicitly designed to support arbitrary whitelisted ERC-20/TRC-20 tokens (Tron's TRC-20 ecosystem includes tokens with non-standard-compliant transfer semantics), and the withdrawal path is triggered automatically by any relayer delivering a valid proof for RedeemEscrow/RefundEscrow, this is readily reachable without any special privilege — only requiring the intent/token combination and a legitimate relayed fill/refund/timeout message.

### Recommendation
Replace the raw `.call(abi.encodeWithSelector(IERC20.transfer.selector, ...))` + `success`-only check in `withdraw()` and the `SweepDust` branch of `onAccept()` with `SafeERC20.safeTransfer()` (the contract already imports and uses `SafeERC20` elsewhere in the file), so both call-success and return-value truthiness (or absence of return data, per EIP-20 ambiguity) are enforced consistently with the rest of the contract.

### Proof of Concept
1. Admin/governance whitelists a TRC-20/ERC-20 token `T` that returns `false` on transfer failure instead of reverting (e.g., a token with a paused/blacklist check that returns `bool` without reverting) as an intent input asset.
2. A user places an order escrowing `T` via `placeOrder`, recorded in `_orders[commitment][T]`.
3. `T` becomes unable to fulfill the transfer to the beneficiary at redemption time (e.g., contract-level pause, blacklist, or balance drained by another interaction) such that `transfer()` returns `false` without reverting.
4. A relayer submits a valid RedeemEscrow/RefundEscrow proof; `onAccept` → `withdraw()` executes `token.call(abi.encodeWithSelector(IERC20.transfer.selector, beneficiary, amount))`; the low-level call succeeds (`success == true`) even though `T.transfer` internally returned `false` and moved no tokens.
5. `_orders[commitment][T] -= amount` decrements escrow state to zero, `EscrowReleased`/`EscrowRefunded` is emitted, but the beneficiary's balance of `T` is unchanged — funds are permanently stuck in the `IntentGatewayV2` contract with no way to re-trigger withdrawal since the escrow record is already cleared.

### Citations

**File:** evm/tron/contracts/apps/IntentGatewayV2.sol (L38-41)
```text
import {IERC20} from "@openzeppelin/contracts/token/ERC20/IERC20.sol";
import {SafeERC20} from "@openzeppelin/contracts/token/ERC20/utils/SafeERC20.sol";
import {ECDSA} from "@openzeppelin/contracts/utils/cryptography/ECDSA.sol";
import {EIP712} from "@openzeppelin/contracts/utils/cryptography/EIP712.sol";
```

**File:** evm/tron/contracts/apps/IntentGatewayV2.sol (L391-411)
```text

            // Transfer all predispatch assets to the call dispatcher
            uint256 assetsLen = order.predispatch.assets.length;
            for (uint256 i; i < assetsLen;) {
                address token = address(uint160(uint256(order.predispatch.assets[i].token)));
                uint256 amount = order.predispatch.assets[i].amount;

                if (token == address(0)) {
                    if (amount > msgValue) revert InsufficientNativeToken();
                    msgValue -= amount;

                    (bool sent,) = dispatcher.call{value: amount}("");
                    if (!sent) revert InsufficientNativeToken();
                } else {
                    IERC20(token).safeTransferFrom(msg.sender, dispatcher, amount);
                }

                unchecked {
                    ++i;
                }
            }
```

**File:** evm/tron/contracts/apps/IntentGatewayV2.sol (L629-635)
```text
    function onAccept(IncomingPostRequest calldata incoming) external override onlyHost {
        RequestKind kind = RequestKind(uint8(incoming.request.body[0]));
        if (kind == RequestKind.RedeemEscrow || kind == RequestKind.RefundEscrow) {
            authenticate(incoming.request);
            WithdrawalRequest memory body = abi.decode(incoming.request.body[1:], (WithdrawalRequest));
            return withdraw(body, kind == RequestKind.RefundEscrow);
        }
```

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

**File:** evm/tron/contracts/apps/IntentGatewayV2.sol (L702-710)
```text
            if (token == address(0)) {
                (bool sent,) = beneficiary.call{value: amount}("");
                if (!sent) revert InsufficientNativeToken();
            } else {
                (bool success,) = token.call(abi.encodeWithSelector(IERC20.transfer.selector, beneficiary, amount));
                if (!success) revert TransferFailed();
            }

            _orders[body.commitment][token] -= amount;
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

**File:** evm/tron/contracts/apps/IntentGatewayV2.sol (L738-743)
```text
    function onGetResponse(IncomingGetResponse calldata incoming) external override onlyHost {
        if (incoming.response.values[0].value.length != 0) revert Filled();

        WithdrawalRequest memory body = abi.decode(incoming.response.request.context, (WithdrawalRequest));
        withdraw(body, true);
    }
```
