## Analysis

The Tron deployment of the IntentGateway diverges from the rest of the codebase's ERC20 handling pattern. While `evm/src/apps/IntentGatewayV2.sol`, `evm/src/apps/intentsv2/IntentsBase.sol`, and the SDK's HyperFungibleToken contracts consistently use OpenZeppelin's `SafeERC20.safeTransfer`/`safeTransferFrom` (which decode and validate the boolean return value), the Tron variant's `withdraw()` and `SweepDust` handler use raw low-level `.call()` and only check that the *call itself* didn't revert — never inspecting the ABI-encoded boolean return data of the `transfer` call.

### Title
Unchecked ERC20 `transfer` return value in `IntentGatewayV2.withdraw()`/`SweepDust` permanently freezes escrowed funds for non-reverting-on-failure tokens - ([File: evm/tron/contracts/apps/IntentGatewayV2.sol])

### Summary
`withdraw()` and the `SweepDust` branch of `onAccept()` in the Tron `IntentGatewayV2` release escrowed ERC20 tokens using a raw `token.call(abi.encodeWithSelector(IERC20.transfer.selector, ...))` and only check the low-level `success` boolean, not the token's own returned success flag. For an ERC20 that signals failure by returning `false` instead of reverting, the outer state (escrow debit, `_filled` marker, fee accounting) advances as if the transfer succeeded even though no tokens moved, permanently freezing the beneficiary's funds.

### Finding Description
In `withdraw()`:
```solidity
(bool success,) = token.call(abi.encodeWithSelector(IERC20.transfer.selector, beneficiary, amount));
if (!success) revert TransferFailed();
_orders[body.commitment][token] -= amount;
``` [1](#0-0) 

and in the `SweepDust` handling inside `onAccept()`:
```solidity
(bool success,) = token.call(abi.encodeWithSelector(IERC20.transfer.selector, req.beneficiary, amount));
if (!success) revert TransferFailed();
``` [2](#0-1) 

`success` here only reflects whether the low-level call reverted — it says nothing about the boolean return value that ERC20 `transfer` is supposed to encode. Non-reverting-on-failure tokens (returning `false` on failure, e.g. due to a blacklist, paused state, or non-standard implementation) will make this call succeed (`success == true`) with `data` decoding to `false`, while the actual balance never moves.

Because the code never decodes/checks that boolean, `withdraw()` proceeds to decrement `_orders[body.commitment][token] -= amount` and set `_filled[body.commitment] = beneficiary`, permanently marking the escrow as settled. There is no other code path to recover these tokens: `withdraw()` guards re-entry with `if (_orders[body.commitment][token] == 0) revert UnknownOrder();`, so once the entry is zeroed the tokens sitting in the contract for that commitment become permanently unreachable to the intended beneficiary. `withdraw()` is reached from the unprivileged `RedeemEscrow`/`RefundEscrow` ISMP request path — i.e., any relayer delivering a message following a user's `fillOrder`/`cancelOrder` call on the paired chain — so this is reachable from a normal user/solver action plus a routine relay, not a privileged operation:
```solidity
function onAccept(IncomingPostRequest calldata incoming) external override onlyHost {
    RequestKind kind = RequestKind(uint8(incoming.request.body[0]));
    if (kind == RequestKind.RedeemEscrow || kind == RequestKind.RefundEscrow) {
        authenticate(incoming.request);
        WithdrawalRequest memory body = abi.decode(incoming.request.body[1:], (WithdrawalRequest));
        return withdraw(body, kind == RequestKind.RefundEscrow);
    }
``` [3](#0-2) 

This directly contrasts with the sibling implementation used elsewhere in the codebase, which correctly relies on `SafeERC20`:
```solidity
if (token == address(0)) {
    _sendValue(beneficiary, amount);
} else {
    IERC20(token).safeTransfer(beneficiary, amount);
}
``` [4](#0-3) 

The Tron contract itself even imports and aliases `SafeERC20` (`using SafeERC20 for IERC20;`) and uses `safeTransferFrom` correctly during `placeOrder` (escrow intake), but reverts to the unsafe raw-call pattern specifically for the outbound `withdraw`/`SweepDust` paths [5](#0-4) [6](#0-5) .

### Impact Explanation
If any input/fee token accepted by this Tron gateway deployment is (or later becomes, e.g. via blacklisting) a non-reverting-on-failure ERC20, both order fills and order cancellations settle successfully in gateway state while the beneficiary receives nothing. The escrow accounting is decremented and the commitment is marked filled/refunded, so the funds cannot be re-claimed through any other function — they are permanently stuck in the contract. This is a permanent freezing-of-funds condition affecting real user/solver escrow, matching Medium/High severity per the validation criteria (concrete permanent freezing of funds).

### Likelihood Explanation
Likelihood depends on the token(s) actually deployed/whitelisted for this Tron IntentGateway. It requires either (a) deliberately supporting a non-standard, non-reverting ERC20 as collateral/input, or (b) a normally-compliant token entering a state where it returns `false` instead of reverting (e.g., certain USDT-style tokens on blacklist/pause conditions, or Tron's TRC20 token ecosystem where non-reverting semantics are historically common). Given Tron's TRC20 ecosystem has a documented history of tokens with non-standard/legacy ERC20 semantics, and this is the Tron-specific contract, the practical likelihood is non-trivial.

### Recommendation
Replace the raw `.call(abi.encodeWithSelector(IERC20.transfer.selector, ...))` + `success`-only check in `withdraw()` (lines 706-708, 720-721) and the `SweepDust` handler (line 674-675) with `IERC20(token).safeTransfer(beneficiary, amount)` using the already-imported `SafeERC20` library, consistent with the rest of the contract's `safeTransferFrom` usage and with `IntentsBase.sol`'s `_withdraw()`.

### Proof of Concept
1. Deploy/whitelist a token `EvilToken` on the Tron gateway whose `transfer()` returns `false` (instead of reverting) when the recipient is denylisted or under some failure condition, without reverting.
2. A user calls `placeOrder` escrowing `EvilToken` as an input, targeting a cross-chain fill.
3. A solver fills the order on the destination chain; a relayer delivers the `RedeemEscrow` message, invoking `onAccept` → `withdraw()` on the Tron source chain.
4. Suppose the solver's beneficiary address is denylisted by `EvilToken` (or the token is paused) at settlement time, causing `EvilToken.transfer` to return `false` without reverting.
5. `token.call(...)` returns `success = true` (only the call succeeded, not the transfer). The code does not decode/verify the returned `false`, so `if (!success) revert TransferFailed();` does not trigger.
6. `_orders[body.commitment][token] -= amount;` executes, zeroing the escrow entry and finalizing `_filled[body.commitment] = beneficiary`.
7. The `EvilToken` balance remains in the `IntentGatewayV2` contract forever — the solver never receives it, and no function permits withdrawing it again for that commitment, since `withdraw()`'s guard `if (_orders[body.commitment][token] == 0) revert UnknownOrder();` now blocks any retry.

### Citations

**File:** evm/tron/contracts/apps/IntentGatewayV2.sol (L55-56)
```text
contract IntentGatewayV2 is HyperApp, EIP712 {
    using SafeERC20 for IERC20;
```

**File:** evm/tron/contracts/apps/IntentGatewayV2.sol (L405-406)
```text
                    IERC20(token).safeTransferFrom(msg.sender, dispatcher, amount);
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

**File:** evm/tron/contracts/apps/IntentGatewayV2.sol (L674-675)
```text
                    (bool success,) = token.call(abi.encodeWithSelector(IERC20.transfer.selector, req.beneficiary, amount));
                    if (!success) revert TransferFailed();
```

**File:** evm/tron/contracts/apps/IntentGatewayV2.sol (L706-710)
```text
                (bool success,) = token.call(abi.encodeWithSelector(IERC20.transfer.selector, beneficiary, amount));
                if (!success) revert TransferFailed();
            }

            _orders[body.commitment][token] -= amount;
```

**File:** evm/src/apps/intentsv2/IntentsBase.sol (L465-469)
```text
            if (token == address(0)) {
                _sendValue(beneficiary, amount);
            } else {
                IERC20(token).safeTransfer(beneficiary, amount);
            }
```
