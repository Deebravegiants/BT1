### Title
Missing Zero-Rate Validation in Token Deposit Allows Silent Fund Loss When Oracle Returns Zero — (File: contracts/pools/RSETHPoolV3.sol)

### Summary
The `deposit(address token, uint256 amount, string referralId)` function in `RSETHPoolV3.sol` and `RSETHPoolV3ExternalBridge.sol` does not validate that the computed `rsETHAmount` is non-zero before minting. If the token's oracle returns a rate of `0`, a depositor's tokens are silently transferred into the pool while they receive `0` wrsETH in return. The same function in the reverse direction (`viewSwapAssetToPremintedRsETH`) explicitly guards against this with zero-rate checks, making the omission in the deposit path a clear inconsistency.

### Finding Description
In `RSETHPoolV3.sol`, `viewSwapRsETHAmountAndFee(uint256 amount, address token)` computes the output as:

```solidity
uint256 tokenToETHRate = IOracle(supportedTokenOracle[token]).getRate();
rsETHAmount = amountAfterFee * tokenToETHRate / rsETHToETHrate;
```

There is no guard on `tokenToETHRate == 0`. If the oracle returns `0`, `rsETHAmount` silently evaluates to `0`. The deposit function then proceeds:

```solidity
IERC20(token).safeTransferFrom(msg.sender, address(this), amount);
(uint256 rsETHAmount, uint256 fee) = viewSwapRsETHAmountAndFee(amount, token);
feeEarnedInToken[token] += fee;
wrsETH.mint(msg.sender, rsETHAmount); // mints 0
```

The user's tokens are transferred in, a fee is recorded, and `mint(msg.sender, 0)` is called — the user receives nothing.

By contrast, the reverse-direction function `viewSwapAssetToPremintedRsETH` in the same contract explicitly validates both rates:

```solidity
if (rsETHToETHrate == 0) revert UnsupportedOracle();
uint256 tokenToETHRate = token == ETH_IDENTIFIER ? 1e18 : IOracle(supportedTokenOracle[token]).getRate();
if (tokenToETHRate == 0) revert UnsupportedOracle();
```

The same inconsistency exists in `RSETHPoolV3ExternalBridge.sol`.

Additionally, unlike the L1 `LRTDepositPool.depositAsset`, which accepts a `minRSETHAmountExpected` slippage guard and reverts if `rsethAmountToMint < minRSETHAmountExpected`, the L2 pool deposit functions provide no minimum-output protection to the caller.

### Impact Explanation
When `tokenToETHRate == 0`, a depositor transfers real ERC-20 tokens into the pool and receives `0` wrsETH. The tokens accumulate in the pool and are subsequently bridged to L1 via `moveAssetsForBridging` or `bridgeTokens`, with no mechanism for the depositor to reclaim them. This constitutes a direct, permanent loss of user funds — matching the **Critical** impact tier (direct theft of user funds in motion).

### Likelihood Explanation
The `addSupportedToken` function validates `IOracle(oracle).getRate() != 0` at registration time, but provides no ongoing guarantee. An oracle can return `0` due to: (1) oracle contract malfunction or upgrade, (2) the underlying price feed going stale or being deprecated, or (3) a transient edge case in the oracle's computation. Because the deposit path has no guard, any such event during a live deposit silently drains the user. Likelihood is **Low** in isolation but the consequence is irreversible, and the missing check is trivially fixable.

### Recommendation
Add a zero-amount guard in `viewSwapRsETHAmountAndFee(uint256 amount, address token)` consistent with `viewSwapAssetToPremintedRsETH`:

```solidity
uint256 tokenToETHRate = IOracle(supportedTokenOracle[token]).getRate();
if (tokenToETHRate == 0) revert UnsupportedOracle();
uint256 rsETHToETHrate = getRate();
if (rsETHToETHrate == 0) revert UnsupportedOracle();
```

Additionally, add a `minWrsETHAmountExpected` parameter to the token deposit function (mirroring `LRTDepositPool.depositAsset`) so callers can enforce slippage protection independently of oracle health.

Apply the same fix to `RSETHPoolV3ExternalBridge.sol`.

### Proof of Concept

1. A token (e.g., wstETH) is added via `addSupportedToken` with a valid oracle. Oracle rate is `1.1e18` at registration.
2. The oracle later returns `0` (malfunction, deprecation, or stale feed).
3. Depositor calls `deposit(wstETH, 100e18, "ref")` on `RSETHPoolV3`.
4. `limitDailyMint` modifier calls `viewSwapRsETHAmountAndFee(100e18, wstETH)` → `rsETHAmount = 0`; `dailyMintAmount += 0` — no revert.
5. `amount == 0` check passes (amount is `100e18`).
6. `IERC20(wstETH).safeTransferFrom(msg.sender, address(this), 100e18)` — 100 wstETH leaves the user.
7. `viewSwapRsETHAmountAndFee` returns `rsETHAmount = 0`, `fee = 100e18 * feeBps / 10_000`.
8. `wrsETH.mint(msg.sender, 0)` — user receives nothing.
9. Bridger calls `bridgeTokens(wstETH)` → 100