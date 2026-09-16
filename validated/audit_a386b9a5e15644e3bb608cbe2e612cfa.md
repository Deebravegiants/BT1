### Title
Upgradeable/fee-on-transfer/rebasing underlying tokens can permanently break `WrappedHyperFungibleToken`, freezing bridged funds - (File: `sdk/packages/core/contracts/apps/WrappedHyperFungibleToken.sol`)

### Summary
`WrappedHyperFungibleToken` locks an owner-configured `_underlying` ERC20 on the home chain and unlocks the exact same nominal `amount` on delivery, timeout-refund, or via the peer `HyperFungibleToken` on remote chains. The contract assumes a strict 1:1 relationship between the amount locked in `send()` and the amount available to unlock later. If the configured underlying token's logic can change post-configuration (proxy-upgradeable token, e.g. a TUSD-style asset) to introduce a transfer fee, rebasing, or balance-changing behavior, this invariant breaks, and the pool held by the contract can become insufficient to honor pending unlocks.

### Finding Description
`send()` locks the underlying token from the caller via `safeTransferFrom` and encodes the nominal `params.amount` into the cross-chain `Message`: [1](#0-0) 

On delivery (`onAccept`) or timeout (`onPostRequestTimeout`), the contract unlocks the same nominal `message.amount` via `safeTransfer`, without ever re-checking the contract's actual token balance against outstanding obligations: [2](#0-1) [3](#0-2) 

`_underlying` is set once by the owner via `configure()` and can be any ERC20 address, with no protocol-level check on whether that token is upgradeable, fee-on-transfer, or rebasing: [4](#0-3) 

Because `send()` records `params.amount` as the amount transferred in, but relies on `safeTransferFrom` actually delivering `params.amount` net to the contract, any underlying token whose implementation is later upgraded (proxy-and-implementation pattern like TUSD) to deduct a transfer fee or to rebase balances downward will cause the tokens actually held by `WrappedHyperFungibleToken` to fall below the sum of all outstanding `message.amount` values promised across in-flight and delivered cross-chain messages. The contract has no reserve/solvency accounting and does not use `balanceOf` deltas to compute the true amount received.

### Impact Explanation
Once the underlying's implementation is upgraded to introduce fee-on-transfer or rebasing behavior:
- New `send()` calls under-fund the contract relative to the `amount` encoded in the dispatched message, since `safeTransferFrom` may deliver less than `params.amount` if a fee is deducted, while the message still promises the full nominal `amount` to be unlocked on the destination chain (or on the same chain via `HyperFungibleToken`'s minted equivalent redeemed back through `WrappedHyperFungibleToken`).
- Subsequent legitimate `onAccept` unlocks or `onPostRequestTimeout` refunds for other users can revert because `IERC20(_underlying).safeTransfer(...)` fails when the contract lacks sufficient balance, causing that incoming POST request to be permanently undeliverable (a route unable to deliver messages) and locking the corresponding cross-chain transfer/refund in limbo, since `onAccept`/`onPostRequestTimeout` are the sole recovery paths and both draw from the same insufficient pool.
- This can cascade into insolvency for all holders of the wrapped representation on remote `HyperFungibleToken` deployments, since their minted supply is meant to be fully backed by the locked underlying in `WrappedHyperFungibleToken`, per the documented model.

### Likelihood Explanation
This requires the underlying token to actually change its transfer/balance semantics after being configured — realistic for upgradeable tokens like TUSD, or any token later found to add a fee-on-transfer/rebasing feature, or migrated to a new implementation with a deflationary component. This is not an admin/governance action by Hyperbridge itself, but a change in a third-party asset's proxy implementation that Hyperbridge integrates as `_underlying`, matching the exact bug class in the referenced report (a supported token like TUSD changing behavior via its proxy).

### Recommendation
- Do not assume nominal transfer amounts; measure `balanceOf(address(this))` before and after `safeTransferFrom` in `send()` and encode/use the actual delta as the bridged `amount`.
- Maintain an explicit accounting of total locked/obligated balance and revert `send()`/`onAccept` if the underlying's actual balance would fall short of obligations.
- Consider a token whitelist/allowlist for `_underlying` that excludes tokens with known or possible fee-on-transfer/rebasing/upgradeable behavior, or add a circuit breaker that pauses the contract if actual `balanceOf` deviates unexpectedly from expected obligations (akin to the TUSD adapter freeze-on-upgrade pattern referenced in the report).

### Proof of Concept
1. Owner configures `WrappedHyperFungibleToken` with `_underlying = TUSD` (a proxy-backed token) via `configure()`.
2. Multiple users bridge TUSD via `send()`, each locking `amount_i` 1:1, with messages encoding the full nominal amounts to be unlocked on remote chains/via refunds.
3. TUSD's implementation is upgraded (by its own team, outside Hyperbridge's control) to introduce a 1% transfer fee or a rebase-down event.
4. Contract's actual TUSD balance is now less than the sum of all outstanding `message.amount` obligations already committed in flight.
5. A later `onAccept` (unlock) or `onPostRequestTimeout` (refund) call for an earlier, legitimately pending message reverts in `safeTransfer` due to insufficient balance, permanently freezing that user's funds since no alternate recovery path exists in the contract.

### Citations

**File:** sdk/packages/core/contracts/apps/WrappedHyperFungibleToken.sol (L178-185)
```text
    function configure(WrappedConfigOptions calldata options) external onlyOwner {
        if (_host == address(0)) {
            _host = options.host;
        }
        _dispatcher = options.dispatcher;
        _underlying = options.underlying;
        _isWeth = options.isWeth;
    }
```

**File:** sdk/packages/core/contracts/apps/WrappedHyperFungibleToken.sol (L266-273)
```text
    function send(HyperFungibleToken.SendParams calldata params) external payable whenNotPaused {
        uint256 msgValue = msg.value;
        if (_isWeth && msgValue >= params.amount) {
            msgValue = msgValue - params.amount;
            IWETH(_underlying).deposit{value: params.amount}();
        } else {
            IERC20(_underlying).safeTransferFrom(msg.sender, address(this), params.amount);
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

**File:** sdk/packages/core/contracts/apps/WrappedHyperFungibleToken.sol (L344-362)
```text
    function onPostRequestTimeout(PostRequestTimeout calldata incoming) external override onlyHost whenNotPaused {
        HyperFungibleToken.Message memory message = abi.decode(incoming.request.body, (HyperFungibleToken.Message));
        address refundee = _toAddr(message.from);

        if (_isWeth) {
            // Try a native-ETH push first; if the refundee cannot accept native value
            // (e.g. the caller used the ERC-20 deposit path in `send()` from a
            // non-payable contract), re-wrap the withdrawn ETH and deliver the
            // underlying WETH as an ERC-20 transfer so the timeout still settles and
            // funds are not permanently locked.
            IWETH(_underlying).withdraw(message.amount);
            (bool sent,) = refundee.call{value: message.amount}("");
            if (!sent) {
                IWETH(_underlying).deposit{value: message.amount}();
                IERC20(_underlying).safeTransfer(refundee, message.amount);
            }
        } else {
            IERC20(_underlying).safeTransfer(refundee, message.amount);
        }
```
