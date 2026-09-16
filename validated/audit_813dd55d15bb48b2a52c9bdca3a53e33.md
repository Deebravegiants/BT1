### Title
Unsafe raw ERC20 `transfer()` in the Tron `IntentGatewayV2` — low-level `call` success is checked but the ERC20 boolean return value is not decoded/verified - (File: `evm/tron/contracts/apps/IntentGatewayV2.sol`)

### Summary
The Tron variant of `IntentGatewayV2` performs ERC20 transfers via raw low-level `.call(abi.encodeWithSelector(IERC20.transfer.selector, ...))` and only checks that the external call itself succeeded (`success == true`), never decoding/validating the ABI-encoded boolean return value that ERC20's `transfer()` is supposed to return. This is exactly the unsafe-`ERC20.transfer()` bug class from the referenced Derby report: tokens that return `false` on failure instead of reverting will make these calls report `success == true` even though no tokens were actually moved.

### Finding Description
In `evm/tron/contracts/apps/IntentGatewayV2.sol`, escrow release (`withdraw`), protocol dust sweeping (`SweepDust` handling), and internal balance-sweep calls all move tokens using:

```solidity
(bool success,) = token.call(abi.encodeWithSelector(IERC20.transfer.selector, beneficiary, amount));
if (!success) revert TransferFailed();
``` [1](#0-0) 

This pattern is repeated for:
- Escrow redemption to the order beneficiary [2](#0-1) 
- Transaction-fee redemption to the beneficiary [3](#0-2) 
- `SweepDust` requests dispatched by the trusted hyperbridge host [4](#0-3) 
- Internal predispatch/sweep calldata construction that is later executed via `ICallDispatcher.dispatch` [5](#0-4) 

The `CallDispatcher.dispatch` function used to execute the sweep `Call[]` batches has the exact same weakness — it only checks the raw call's `success` flag, never the ABI-decoded boolean payload:

```solidity
(bool success, bytes memory result) = to.call{value: call.value}(call.data);
if (!success) revert CallFailed(to, result);
``` [6](#0-5) 

Contrast this with the canonical EVM `IntentGatewayV2`/`IntentsBase` implementation, which consistently uses OpenZeppelin's `SafeERC20.safeTransfer`/`safeTransferFrom`, correctly handling both reverting and non-reverting-but-`false`-returning tokens: [7](#0-6) 

The Tron contract, however, does not use `SafeERC20` for its outbound transfers on the withdraw/sweep code paths, despite importing `SafeERC20` for `safeTransferFrom` on the inbound deposit path [8](#0-7) .

### Impact Explanation
If a non-standard ERC20 token that returns `false` instead of reverting on a failed `transfer` (e.g. due to insufficient allowance edge cases, paused transfers, blacklist checks, or a non-compliant token implementation) is used as an intent input/output/fee token on the Tron deployment:
- `withdraw()` will mark the order as filled (`_filled[body.commitment] = beneficiary`) and decrement the internal escrow accounting (`_orders[body.commitment][token] -= amount`) even though the beneficiary received nothing, permanently freezing/losing the escrowed funds inside the contract with no way to re-claim them (state says filled/zeroed, but tokens remain stuck).
- `SweepDust` operations dispatched by the host would similarly report success and emit `DustSwept` events without any tokens actually moving, misleading protocol accounting and potentially trapping dust funds in the contract permanently.

This satisfies "permanent freezing of funds" — the escrow bookkeeping is decremented/finalized on the assumption a transfer succeeded, so the underlying tokens become permanently unrecoverable when the token silently fails.

### Likelihood Explanation
This path is reachable by any solver/user filling or refunding an intent order whose input, output, or fee token is a non-standard ERC20 that returns `false` on failure (a known category of tokens in production, e.g. some legacy/deflationary/pausable tokens). No privileged role is required — a regular relayed `RedeemEscrow`/`RefundEscrow` incoming request (validated via `authenticate`) or a hyperbridge-originated `SweepDust` request triggers the vulnerable code. Likelihood is Medium: it depends on the specific ERC20 token configured for an intent order being one of the small set of non-compliant, non-reverting tokens, but no attacker privilege or complex setup is otherwise needed.

### Recommendation
Replace all raw `token.call(abi.encodeWithSelector(IERC20.transfer.selector, ...))` patterns in `evm/tron/contracts/apps/IntentGatewayV2.sol` with OpenZeppelin's `SafeERC20.safeTransfer`, consistent with the canonical EVM implementation in `evm/src/apps/intentsv2/IntentsBase.sol`. This applies to the `withdraw()` function (escrow and fee redemption), the `SweepDust` handling branch, and the predispatch/sweep `Call` construction sites. Additionally, `CallDispatcher.dispatch` in `evm/src/utils/CallDispatcher.sol` should either be restricted from being used to move ERC20 tokens directly, or callers should independently verify balances before/after (as `IntentsBase._execute` already does) rather than relying solely on `success`.

### Proof of Concept
1. Deploy an ERC20 token whose `transfer` function returns `false` on failure instead of reverting (e.g., insufficient balance triggers `return false;` rather than a revert) as the input token for an intent order on the Tron `IntentGatewayV2`.
2. Place an order, have it filled cross-chain, and trigger the `RedeemEscrow` incoming request path calling `withdraw()`.
3. Arrange for the token transfer inside `token.call(abi.encodeWithSelector(IERC20.transfer.selector, beneficiary, amount))` to return `false` (e.g., temporarily pause transfers via the token's admin function, or trigger a blacklist condition on the beneficiary) while the low-level call itself does not revert.
4. Observe that `success == true` (the call executed without reverting), so `withdraw()` proceeds to decrement `_orders[body.commitment][token]` and mark `_filled[body.commitment] = beneficiary`, finalizing the order — even though the beneficiary's token balance did not change and the tokens remain stuck in the `IntentGatewayV2` contract with no remaining code path to reclaim them.

### Citations

**File:** evm/tron/contracts/apps/IntentGatewayV2.sol (L38-41)
```text
import {IERC20} from "@openzeppelin/contracts/token/ERC20/IERC20.sol";
import {SafeERC20} from "@openzeppelin/contracts/token/ERC20/utils/SafeERC20.sol";
import {ECDSA} from "@openzeppelin/contracts/utils/cryptography/ECDSA.sol";
import {EIP712} from "@openzeppelin/contracts/utils/cryptography/EIP712.sol";
```

**File:** evm/tron/contracts/apps/IntentGatewayV2.sol (L427-435)
```text
                } else {
                    balance = IERC20(token).balanceOf(dispatcher);
                    if (balance < requiredAmount) revert InvalidInput();
                    transferCalls[i] = Call({
                        to: token,
                        value: 0,
                        data: abi.encodeWithSelector(IERC20.transfer.selector, address(this), balance)
                    });
                }
```

**File:** evm/tron/contracts/apps/IntentGatewayV2.sol (L673-676)
```text
                } else {
                    (bool success,) = token.call(abi.encodeWithSelector(IERC20.transfer.selector, req.beneficiary, amount));
                    if (!success) revert TransferFailed();
                }
```

**File:** evm/tron/contracts/apps/IntentGatewayV2.sol (L702-722)
```text
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

**File:** evm/src/utils/CallDispatcher.sol (L59-60)
```text
            (bool success, bytes memory result) = to.call{value: call.value}(call.data);
            if (!success) revert CallFailed(to, result);
```

**File:** evm/src/apps/intentsv2/IntentsBase.sol (L464-469)
```text
            _orders[body.commitment][token] = escrowed - amount;
            if (token == address(0)) {
                _sendValue(beneficiary, amount);
            } else {
                IERC20(token).safeTransfer(beneficiary, amount);
            }
```
