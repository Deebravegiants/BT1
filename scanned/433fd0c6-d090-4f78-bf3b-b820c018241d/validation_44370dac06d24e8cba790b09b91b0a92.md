### Title
Missing Oracle Rate Zero-Validation Before Division in `deposit` Causes Temporary Fund Freeze - (File: contracts/pools/RSETHPoolV2NBA.sol)

---

### Summary

`RSETHPoolV2NBA.viewSwapRsETHAmountAndFee` divides by `rsETHToETHrate` fetched from `IOracle(rsETHOracle).getRate()` without validating that the returned rate is non-zero. If the oracle returns zero, every call to `deposit` reverts with a division-by-zero panic, permanently blocking all user deposits until the oracle is replaced.

---

### Finding Description

In `RSETHPoolV2NBA`, the `deposit` function calls `viewSwapRsETHAmountAndFee`, which fetches the oracle rate and immediately uses it as a divisor:

```solidity
uint256 rsETHToETHrate = getRate();
rsETHAmount = amountAfterFee * 1e18 / rsETHToETHrate;  // panics if rsETHToETHrate == 0
``` [1](#0-0) 

`getRate()` is a thin pass-through with no validation:

```solidity
function getRate() public view returns (uint256) {
    return IOracle(rsETHOracle).getRate();
}
``` [2](#0-1) 

`setRSETHOracle` only enforces a non-zero address, not a non-zero rate:

```solidity
function setRSETHOracle(address _rsETHOracle) external onlyRole(DEFAULT_ADMIN_ROLE) {
    UtilLib.checkNonZeroAddress(_rsETHOracle);
    rsETHOracle = _rsETHOracle;
``` [3](#0-2) 

This is in direct contrast to the V3 pool contracts, which explicitly guard against a zero rate at oracle registration time:

```solidity
if (IOracle(oracle).getRate() == 0) {
    revert UnsupportedOracle();
}
``` [4](#0-3) 

The same unguarded division pattern also appears in `RSETHPoolV2.sol`, `RSETHPoolV2ExternalBridge.sol`, `RSETHPool.sol`, `RSETHPoolNoWrapper.sol`, and `RSETHPoolV3WithNativeChainBridge.sol` in their respective `viewSwapRsETHAmountAndFee` functions. [5](#0-4) [6](#0-5) 

---

### Impact Explanation

If `getRate()` returns zero — due to a misconfigured oracle being set, an oracle contract bug, or a Chainlink feed returning a zero/negative answer that is not caught by the oracle wrapper — every call to `deposit` reverts with `panic: division or modulo by zero (0x12)`. All user ETH sent to the pool is locked until the oracle is corrected. This constitutes **temporary freezing of funds** (Medium severity per the allowed scope).

---

### Likelihood Explanation

The `setRSETHOracle` function accepts any non-zero address without rate validation. A misconfigured oracle address (e.g., pointing to a contract whose `getRate()` returns 0 at deployment or after an upgrade) can be set without any on-chain guard. The `ChainlinkPriceOracle` used in the core protocol does not validate the Chainlink answer against zero before returning it:

```solidity
(, int256 price,,,) = priceFeed.latestRoundData();
return uint256(price) * 1e18 / 10 ** uint256(priceFeed.decimals());
``` [7](#0-6) 

Likelihood is **low** (requires oracle misconfiguration or oracle-level failure), but the missing guard is a clear code-level defect with a concrete, reproducible impact path.

---

### Recommendation

Add a zero-rate guard in `viewSwapRsETHAmountAndFee` before the division, mirroring the pattern already used in `viewSwapAssetToPremintedRsETH` in the V3 contracts:

```solidity
uint256 rsETHToETHrate = getRate();
if (rsETHToETHrate == 0) revert InvalidRate();
rsETHAmount = amountAfterFee * 1e18 / rsETHToETHrate;
```

Additionally, add the same rate-validity check to `setRSETHOracle` (and the `initialize` function) in `RSETHPoolV2NBA`, `RSETHPoolV2`, `RSETHPoolV2ExternalBridge`, `RSETHPool`, `RSETHPoolNoWrapper`, and `RSETHPoolV3WithNativeChainBridge`.

---

### Proof of Concept

1. Deploy `RSETHPoolV2NBA` with a mock oracle whose `getRate()` returns `0`.
2. Call `deposit{value: 1 ether}("ref")` from any EOA.
3. The call reverts with `panic: division or modulo by zero (0x12)` inside `viewSwapRsETHAmountAndFee` at the line `rsETHAmount = amountAfterFee * 1e18 / rsETHToETHrate`.
4. All subsequent deposits are blocked until the oracle is replaced by the admin. [8](#0-7)

### Citations

**File:** contracts/pools/RSETHPoolV2NBA.sol (L100-102)
```text
    function getRate() public view returns (uint256) {
        return IOracle(rsETHOracle).getRate();
    }
```

**File:** contracts/pools/RSETHPoolV2NBA.sol (L106-133)
```text
    function deposit(string memory referralId) external payable nonReentrant whenNotPaused {
        uint256 amount = msg.value;

        if (amount == 0) revert InvalidAmount();

        (uint256 rsETHAmount, uint256 fee) = viewSwapRsETHAmountAndFee(amount);

        feeEarnedInETH += fee;

        wrsETH.mint(msg.sender, rsETHAmount);

        emit SwapOccurred(msg.sender, rsETHAmount, fee, referralId);
    }

    /// @dev view function to get the rsETH amount for a given amount of ETH
    /// @param amount The amount of ETH
    /// @return rsETHAmount The amount of rsETH that will be received
    /// @return fee The fee that will be charged
    function viewSwapRsETHAmountAndFee(uint256 amount) public view returns (uint256 rsETHAmount, uint256 fee) {
        fee = amount * feeBps / 10_000;
        uint256 amountAfterFee = amount - fee;

        // rate of rsETH in ETH
        uint256 rsETHToETHrate = getRate();

        // Calculate the final rsETH amount
        rsETHAmount = amountAfterFee * 1e18 / rsETHToETHrate;
    }
```

**File:** contracts/pools/RSETHPoolV2NBA.sol (L171-174)
```text
    function setRSETHOracle(address _rsETHOracle) external onlyRole(DEFAULT_ADMIN_ROLE) {
        UtilLib.checkNonZeroAddress(_rsETHOracle);
        rsETHOracle = _rsETHOracle;
        emit OracleSet(_rsETHOracle);
```

**File:** contracts/pools/RSETHPoolV3.sol (L548-550)
```text
        if (IOracle(oracle).getRate() == 0) {
            revert UnsupportedOracle();
        }
```

**File:** contracts/pools/RSETHPoolV2.sol (L225-234)
```text
    function viewSwapRsETHAmountAndFee(uint256 amount) public view returns (uint256 rsETHAmount, uint256 fee) {
        fee = amount * feeBps / 10_000;
        uint256 amountAfterFee = amount - fee;

        // rate of rsETH in ETH
        uint256 rsETHToETHrate = getRate();

        // Calculate the final rsETH amount
        rsETHAmount = amountAfterFee * 1e18 / rsETHToETHrate;
    }
```

**File:** contracts/pools/RSETHPoolNoWrapper.sol (L277-286)
```text
    function viewSwapRsETHAmountAndFee(uint256 amount) public view returns (uint256 rsETHAmount, uint256 fee) {
        fee = amount * feeBps / 10_000;
        uint256 amountAfterFee = amount - fee;

        // rate of rsETH in ETH
        uint256 rsETHToETHrate = getRate();

        // Calculate the final rsETH amount
        rsETHAmount = amountAfterFee * 1e18 / rsETHToETHrate;
    }
```

**File:** contracts/oracles/ChainlinkPriceOracle.sol (L52-54)
```text
        (, int256 price,,,) = priceFeed.latestRoundData();

        return uint256(price) * 1e18 / 10 ** uint256(priceFeed.decimals());
```
