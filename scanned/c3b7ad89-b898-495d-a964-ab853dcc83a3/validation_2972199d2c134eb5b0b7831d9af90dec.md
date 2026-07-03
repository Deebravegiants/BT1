### Title
Token Oracle Zero-Return Causes Silent Fund Theft in L2 Pool Token Deposits - (File: contracts/pools/RSETHPoolV3.sol)

### Summary

In `RSETHPoolV3.viewSwapRsETHAmountAndFee(uint256 amount, address token)` and the equivalent function in every other L2 pool variant (`RSETHPool`, `RSETHPoolNoWrapper`, `RSETHPoolV3ExternalBridge`, `RSETHPoolV3WithNativeChainBridge`), the `tokenToETHRate` fetched from the token's oracle is used directly in the rsETH amount calculation without a zero-value guard. If the oracle returns zero at deposit time, the user's tokens are silently transferred into the pool while zero rsETH is minted — a complete, unrecoverable loss of the deposited funds.

### Finding Description

Every L2 pool's token deposit path calls `viewSwapRsETHAmountAndFee(amount, token)`:

```solidity
// RSETHPoolV3.sol lines 315-335
function viewSwapRsETHAmountAndFee(
    uint256 amount,
    address token
) public view onlySupportedToken(token) returns (uint256 rsETHAmount, uint256 fee) {
    fee = amount * feeBps / 10_000;
    uint256 amountAfterFee = amount - fee;

    uint256 rsETHToETHrate = getRate();

    // rate of token in ETH — NO ZERO CHECK
    uint256 tokenToETHRate = IOracle(supportedTokenOracle[token]).getRate();

    // If tokenToETHRate == 0, rsETHAmount == 0
    rsETHAmount = amountAfterFee * tokenToETHRate / rsETHToETHrate;
}
``` [1](#0-0) 

The calling deposit function then:
1. Transfers the user's tokens into the pool
2. Mints `rsETHAmount` (which is 0) to the user
3. Emits a `SwapOccurred` event with `rsETHAmount = 0`

```solidity
// RSETHPoolV3.sol lines 271-293
IERC20(token).safeTransferFrom(msg.sender, address(this), amount); // tokens taken
(uint256 rsETHAmount, uint256 fee) = viewSwapRsETHAmountAndFee(amount, token);
feeEarnedInToken[token] += fee;
wrsETH.mint(msg.sender, rsETHAmount); // mints 0
``` [2](#0-1) 

The deposit function accepts no `minRsETHAmountExpected` parameter, so the user has no slippage protection. The tokens are now held by the pool with no mechanism for the depositor to recover them.

The same unguarded pattern exists in all pool variants: [3](#0-2) [4](#0-3) [5](#0-4) [6](#0-5) 

The inconsistency is stark: the **reverse swap** path (`viewSwapAssetToPremintedRsETH`) in the same contracts already guards against a zero oracle rate:

```solidity
// RSETHPoolV3.sol lines 392-397
uint256 rsETHToETHrate = getRate();
if (rsETHToETHrate == 0) revert UnsupportedOracle();

uint256 tokenToETHRate = token == ETH_IDENTIFIER ? 1e18 : IOracle(supportedTokenOracle[token]).getRate();
if (tokenToETHRate == 0) revert UnsupportedOracle();
``` [7](#0-6) 

The forward deposit path has no equivalent guard.

The oracle is validated at setup time (`addSupportedToken`) and update time (`setSupportedTokenOracle`) to be non-zero:

```solidity
if (IOracle(oracle).getRate() == 0) {
    revert UnsupportedOracle();
}
``` [8](#0-7) 

However, this is a point-in-time check. The oracle can return zero after being set — for example, if the underlying price feed returns zero, if the oracle contract is upgraded to a buggy implementation, or if the oracle's data source becomes unavailable. The `ChainlinkPriceOracle` used on mainnet does not check for zero:

```solidity
// ChainlinkPriceOracle.sol lines 49-55
function getAssetPrice(address asset) external view onlySupportedAsset(asset) returns (uint256) {
    AggregatorV3Interface priceFeed = AggregatorV3Interface(assetPriceFeed[asset]);
    (, int256 price,,,) = priceFeed.latestRoundData();
    return uint256(price) * 1e18 / 10 ** uint256(priceFeed.decimals());
}
``` [9](#0-8) 

### Impact Explanation

**Critical — Direct theft of user funds.**

When `tokenToETHRate == 0`:
- The user's full token deposit is transferred to the pool contract.
- Zero wrsETH is minted to the user.
- The tokens are absorbed into the pool's balance and subsequently moved to the bridge by the `BRIDGER_ROLE`, making them unrecoverable by the depositor.
- There is no minimum-output parameter in the deposit function to protect the user.

### Likelihood Explanation

**Low.** The oracle is validated to be non-zero at setup and update time. However, the oracle is an external dependency that can return zero after being set — due to a Chainlink feed returning zero (no zero-price guard in `ChainlinkPriceOracle`), an oracle upgrade introducing a bug, or a data source outage. The external report's judge accepted this class of risk as sufficient for Medium severity when demonstrated for a similar oracle dependency.

### Recommendation

Add a zero-value guard for `tokenToETHRate` in `viewSwapRsETHAmountAndFee(uint256 amount, address token)` in all pool contracts, mirroring the guard already present in `viewSwapAssetToPremintedRsETH`:

```solidity
uint256 tokenToETHRate = IOracle(supportedTokenOracle[token]).getRate();
if (tokenToETHRate == 0) revert UnsupportedOracle();
```

Additionally, consider adding a `minRsETHAmountExpected` parameter to the token deposit function to give users slippage protection.

### Proof of Concept

1. A token oracle (e.g., for wstETH) is set on `RSETHPoolV3` via `addSupportedToken`. At setup time, `getRate()` returns a valid non-zero value.
2. At a later time, the oracle's underlying price feed returns 0 (e.g., Chainlink returns 0 for the asset).
3. A user calls `deposit(wstETH, 10 ether, "ref")`.
4. `IERC20(wstETH).safeTransferFrom(user, pool, 10 ether)` — 10 wstETH transferred to pool.
5. `viewSwapRsETHAmountAndFee(10 ether, wstETH)` is called:
   - `tokenToETHRate = IOracle(supportedTokenOracle[wstETH]).getRate()` → returns `0`
   - `rsETHAmount = amountAfterFee * 0 / rsETHToETHrate` → `rsETHAmount = 0`
6. `wrsETH.mint(user, 0)` — user receives 0 wrsETH.
7. User has lost 10 wstETH with no recourse.

### Citations

**File:** contracts/pools/RSETHPoolV3.sol (L271-293)
```text
    function deposit(
        address token,
        uint256 amount,
        string memory referralId
    )
        external
        nonReentrant
        whenNotPaused
        onlySupportedToken(token)
        limitDailyMint(amount, token)
    {
        if (amount == 0) revert InvalidAmount();

        IERC20(token).safeTransferFrom(msg.sender, address(this), amount);

        (uint256 rsETHAmount, uint256 fee) = viewSwapRsETHAmountAndFee(amount, token);

        feeEarnedInToken[token] += fee;

        wrsETH.mint(msg.sender, rsETHAmount);

        emit SwapOccurred(msg.sender, rsETHAmount, fee, referralId, token);
    }
```

**File:** contracts/pools/RSETHPoolV3.sol (L315-335)
```text
    function viewSwapRsETHAmountAndFee(
        uint256 amount,
        address token
    )
        public
        view
        onlySupportedToken(token)
        returns (uint256 rsETHAmount, uint256 fee)
    {
        fee = amount * feeBps / 10_000;
        uint256 amountAfterFee = amount - fee;

        // rate of rsETH in ETH
        uint256 rsETHToETHrate = getRate();

        // rate of token in ETH
        uint256 tokenToETHRate = IOracle(supportedTokenOracle[token]).getRate();

        // Calculate the final rsETH amount
        rsETHAmount = amountAfterFee * tokenToETHRate / rsETHToETHrate;
    }
```

**File:** contracts/pools/RSETHPoolV3.sol (L392-397)
```text
        uint256 rsETHToETHrate = getRate();
        if (rsETHToETHrate == 0) revert UnsupportedOracle();

        // Rate of token in ETH
        uint256 tokenToETHRate = token == ETH_IDENTIFIER ? 1e18 : IOracle(supportedTokenOracle[token]).getRate();
        if (tokenToETHRate == 0) revert UnsupportedOracle();
```

**File:** contracts/pools/RSETHPoolV3.sol (L548-550)
```text
        if (IOracle(oracle).getRate() == 0) {
            revert UnsupportedOracle();
        }
```

**File:** contracts/pools/RSETHPool.sol (L340-347)
```text
        uint256 rsETHToETHrate = getRate();

        // rate of token in ETH
        uint256 tokenToETHRate = IOracle(supportedTokenOracle[token]).getRate();

        // Calculate the final rsETH amount
        rsETHAmount = amountAfterFee * tokenToETHRate / rsETHToETHrate;
    }
```

**File:** contracts/pools/RSETHPoolNoWrapper.sol (L305-312)
```text
        uint256 rsETHToETHrate = getRate();

        // rate of token in ETH
        uint256 tokenToETHRate = IOracle(supportedTokenOracle[token]).getRate();

        // Calculate the final rsETH amount
        rsETHAmount = amountAfterFee * tokenToETHRate / rsETHToETHrate;
    }
```

**File:** contracts/pools/RSETHPoolV3ExternalBridge.sol (L446-453)
```text
        uint256 rsETHToETHrate = getRate();

        // rate of token in ETH
        uint256 tokenToETHRate = IOracle(supportedTokenOracle[token]).getRate();

        // Calculate the final rsETH amount
        rsETHAmount = amountAfterFee * tokenToETHRate / rsETHToETHrate;
    }
```

**File:** contracts/pools/RSETHPoolV3WithNativeChainBridge.sol (L364-371)
```text
        uint256 rsETHToETHrate = getRate();

        // rate of token in ETH
        uint256 tokenToETHRate = IOracle(supportedTokenOracle[token]).getRate();

        // Calculate the final rsETH amount
        rsETHAmount = amountAfterFee * tokenToETHRate / rsETHToETHrate;
    }
```

**File:** contracts/oracles/ChainlinkPriceOracle.sol (L49-55)
```text
    function getAssetPrice(address asset) external view onlySupportedAsset(asset) returns (uint256) {
        AggregatorV3Interface priceFeed = AggregatorV3Interface(assetPriceFeed[asset]);

        (, int256 price,,,) = priceFeed.latestRoundData();

        return uint256(price) * 1e18 / 10 ** uint256(priceFeed.decimals());
    }
```
