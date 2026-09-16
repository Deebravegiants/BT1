### Title
Unconditional native-ETH `.call{value: amount}("")` in `IntentGatewayV2.withdraw()`/`SweepDust` handler reverts and permanently freezes escrowed funds when beneficiary is a non-payable contract - (File: `evm/tron/contracts/apps/IntentGatewayV2.sol`)

### Summary
The Tron fork of `IntentGatewayV2` pays out escrowed native ETH to a beneficiary with an unconditional low-level call, `beneficiary.call{value: amount}("")`, and treats any failure as a hard revert (`revert InsufficientNativeToken()`), exactly mirroring the root cause of the referenced Taiko `ERC20Vault` finding: a bridge/escrow contract force-pushing native value to an arbitrary destination address without accounting for recipients that implement neither `receive()` nor a payable `fallback()`.

### Finding Description
`withdraw(WithdrawalRequest memory body, bool isRefund)` in `evm/tron/contracts/apps/IntentGatewayV2.sol` iterates the withdrawal request's token list and, for the native-token entry (`token == address(0)`), does:
```solidity
(bool sent,) = beneficiary.call{value: amount}("");
if (!sent) revert InsufficientNativeToken();
``` [1](#0-0) 
This call is made regardless of whether the beneficiary contract can accept plain ETH transfers. The same pattern recurs in the `SweepDust` request handler in the same file:
```solidity
if (token == address(0)) {
    (bool sent,) = req.beneficiary.call{value: amount}("");
    if (!sent) revert InsufficientNativeToken();
}
``` [2](#0-1) 

Both `withdraw()` and the `SweepDust` handler are invoked from `onAccept`/`onGetResponse`/`onPostRequestTimeout` style entry points that are triggered by relayed ISMP messages, i.e. an unprivileged relayer delivering a proven cross-chain message ultimately drives this call with a `beneficiary` address chosen by the original order's `output.beneficiary` field (attacker/user controlled at order-placement time) — the same "sender/receiver may be a non-payable contract" trust boundary flagged in the Taiko report.

Note that the sibling, non-Tron implementation of this logic in `evm/src/apps/intentsv2/IntentsBase.sol::_withdraw` already guards against this exact class of bug with `if (amount == 0) continue;` before transferring [3](#0-2) , and further uses `_sendValue`, which still reverts on failure but is only reached when `amount != 0`. The Tron fork (`evm/tron/contracts/apps/IntentGatewayV2.sol`) was not updated with this guard, so it retains the unconditional-call defect: any `WithdrawalRequest` or `SweepDust` entry with `token == address(0)` and `amount == 0` (a legitimate no-op case, e.g. an order/fill with a zero native output leg) will still attempt to push 0 ETH to the beneficiary. If that beneficiary is a contract without `receive()`/`fallback()`, the call reverts, and because it's unconditional and not wrapped for a value-only skip, the entire `withdraw`/`onAccept` transaction reverts — for `amount > 0` this is a more classic "beneficiary can't accept ETH" freeze, and for the `amount == 0` case it reproduces the Taiko bug precisely (an unnecessary zero-value push that the caller never intended and that permanently blocks fund release for other tokens escrowed in the same withdrawal batch).

### Impact Explanation
Because `_orders[body.commitment][token]` accounting and the `_filled[body.commitment]` finalization happen in the same function/transaction as the native push, a revert on the ETH leg blocks release of *all* escrowed assets for that order (ERC-20 legs included, since they're processed in the same loop before/after the failing native leg) and also blocks the transaction-fee payout. There is no retry path decoupled from the native transfer inside this contract (unlike the wrapped-token apps, e.g. `WrappedHyperFungibleToken.onAccept`, which explicitly falls back to an ERC-20/WETH transfer on failed native push [4](#0-3) ). Escrowed user/solver funds for the order become permanently stuck — the order is not marked filled/refunded, `_orders` balances remain locked, and the order can never be finalized, matching the "permanent freezing of funds" impact bar.

### Likelihood Explanation
Reachable by any solver/relayer/user in the normal cross-chain intent-fill flow: a user (or a malicious order-placer/solver acting as beneficiary) simply sets `order.output.beneficiary`/`WithdrawalRequest.beneficiary` to a deployed contract address that implements no `receive()`/`fallback()` (e.g., a proxy, a plain logic contract, or one with only non-payable functions). No special privileges are required, and the zero-amount case can be produced deterministically by any order whose output/withdrawal accounting yields a native-token amount of 0 for a leg (or, for `amount > 0`, simply any beneficiary contract lacking a payable fallback). This is a straightforward, low-effort griefing/self-lock vector on the Tron deployment of `IntentGatewayV2`.

### Recommendation
- In `withdraw()` and the `SweepDust` branch of `evm/tron/contracts/apps/IntentGatewayV2.sol`, skip the native transfer entirely when `amount == 0` (mirroring the `if (amount == 0) continue;` guard already present in `evm/src/apps/intentsv2/IntentsBase.sol::_withdraw`).
- For `amount > 0` transfers to a beneficiary lacking `receive()/fallback()`, avoid reverting the whole batch: decouple escrow-accounting/finalization from the native push, or fall back to a pull-based/WETH-wrapped delivery (as done in `WrappedHyperFungibleToken.onAccept`) so a non-payable beneficiary cannot permanently freeze the order's other escrowed assets.

### Proof of Concept
1. Place a cross-chain order on the Tron-deployed `IntentGatewayV2` whose `output`/withdrawal token list includes a native-token (`address(0)`) entry with `amount == 0` (or any nonzero amount) and set the fill/order `beneficiary` to a pre-deployed contract that implements neither `receive()` nor a payable `fallback()` (analogous to the `NoFallback` contract from the original Taiko PoC).
2. Drive the order through to settlement so that `withdraw(body, isRefund)` (or the `SweepDust` `onAccept` path) is invoked with that beneficiary.
3. Observe the transaction reverts at:
```solidity
(bool sent,) = beneficiary.call{value: amount}("");
if (!sent) revert InsufficientNativeToken();
``` [1](#0-0) 
4. Confirm `_orders[body.commitment][*]` balances remain locked and `_filled[body.commitment]` is never finalized — all escrowed assets for the order (native and ERC-20 legs, plus tx fees) are permanently stuck, since no alternate retry/withdraw path exists in this contract for changing the beneficiary or skipping the native leg.

### Citations

**File:** evm/tron/contracts/apps/IntentGatewayV2.sol (L670-672)
```text
                if (token == address(0)) {
                    (bool sent,) = req.beneficiary.call{value: amount}("");
                    if (!sent) revert InsufficientNativeToken();
```

**File:** evm/tron/contracts/apps/IntentGatewayV2.sol (L702-704)
```text
            if (token == address(0)) {
                (bool sent,) = beneficiary.call{value: amount}("");
                if (!sent) revert InsufficientNativeToken();
```

**File:** evm/src/apps/intentsv2/IntentsBase.sol (L456-469)
```text
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
```

**File:** sdk/packages/core/contracts/apps/WrappedHyperFungibleToken.sol (L309-324)
```text
        if (_isWeth) {
            // Try a native-ETH push first (cheap for EOAs and payable contracts);
            // if the recipient cannot accept native value (no `receive()` / `fallback()
            // payable`), re-wrap the withdrawn ETH and deliver the underlying WETH as
            // an ERC-20 transfer instead. This mirrors the deposit-side flexibility of
            // `send()` (which accepts WETH from non-payable callers via `safeTransferFrom`)
            // so the refund path doesn't permanently lock funds for the same caller class.
            IWETH(_underlying).withdraw(message.amount);
            (bool sent,) = beneficiary.call{value: message.amount}("");
            if (!sent) {
                IWETH(_underlying).deposit{value: message.amount}();
                IERC20(_underlying).safeTransfer(beneficiary, message.amount);
            }
        } else {
            IERC20(_underlying).safeTransfer(beneficiary, message.amount);
        }
```
