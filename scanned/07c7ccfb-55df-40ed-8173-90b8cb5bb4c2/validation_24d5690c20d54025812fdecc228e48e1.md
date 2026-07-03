### Title
Stale `ethValueInWithdrawal` Snapshot Causes Incorrect rsETH Price Calculation - (`contracts/LRTConverter.sol`)

### Summary
`LRTConverter.ethValueInWithdrawal` is recorded at the LST oracle price at the moment `transferAssetFromDepositPool()` is called, but the actual ETH value of those LSTs changes as the LST price moves during the unstaking window. Because `ethValueInWithdrawal` is consumed verbatim by `LRTOracle._getTotalEthInProtocol()` as the ETH-denominated value of assets sitting in the converter, the rsETH price is systematically mis-stated for the entire duration of the unstaking period — directly analogous to the reported bug where `_debt_value + _margin_value` was used instead of the current `_position_value`.

### Finding Description

When an operator moves an LST (e.g. stETH) from the deposit pool to the converter for unstaking, `transferAssetFromDepositPool` snapshots the ETH value at the current oracle price:

```solidity
// LRTConverter.sol L140
ethValueInWithdrawal += (_amount * lrtOracle.getAssetPrice(_asset)) / 1e18;
``` [1](#0-0) 

Simultaneously, `getAssetDistributionData` for that LST sets `assetLyingInConverter = 0`, so the LST is no longer counted in the LST-denominated accounting:

```solidity
// LRTDepositPool.sol L460
assetLyingInConverter = 0; // assets in converter are accounted in their eth value => getETHDistributionData()
``` [2](#0-1) 

Instead, its value is supposed to be captured through the ETH-denominated path via `getETHDistributionData`:

```solidity
// LRTDepositPool.sol L498-499
address lrtConverter = lrtConfig.getContract(LRTConstants.LRT_CONVERTER);
ethLyingInConverter = ILRTConverter(lrtConverter).ethValueInWithdrawal();
``` [3](#0-2) 

`_getTotalEthInProtocol()` in `LRTOracle` then multiplies `getTotalAssetDeposits(ETH_TOKEN)` — which includes `ethValueInWithdrawal` — by `getAssetPrice(ETH_TOKEN) = 1e18`:

```solidity
// LRTOracle.sol L339-343
uint256 assetER = getAssetPrice(asset);
uint256 totalAssetAmt = ILRTDepositPool(lrtDepositPoolAddr).getTotalAssetDeposits(asset);
totalETHInProtocol += totalAssetAmt.mulWad(assetER);
``` [4](#0-3) 

The rsETH price is then computed from this total:

```solidity
// LRTOracle.sol L250
uint256 newRsETHPrice = (totalETHInProtocol - protocolFeeInETH).divWad(rsethSupply);
``` [5](#0-4) 

**The root cause:** `ethValueInWithdrawal` is a stale snapshot of the LST's ETH value at the time of transfer. The actual ETH value of the LST changes over time as the LST price moves. So the total ETH in the protocol is incorrectly computed for the entire duration of the unstaking window. This is structurally identical to the reported bug: `_debt_value + _margin_value` was used instead of `_position_value` because the formula did not account for uncorrelated price movements between the debt token and position token. Here, the stale `ethValueInWithdrawal` does not account for price movements of the LST relative to ETH during the unstaking period.

Additionally, `transferAssetToDepositPool` compounds the error by reducing `ethValueInWithdrawal` using the **current** price rather than the original snapshot price, creating a further mismatch:

```solidity
// LRTConverter.sol L160-163
uint256 assetValue = (_amount * lrtOracle.getAssetPrice(_asset)) / 1e18;
ethValueInWithdrawal = ethValueInWithdrawal > assetValue ? ethValueInWithdrawal - assetValue : 0;
``` [6](#0-5) 

### Impact Explanation

- **LST price increases during unstaking:** `ethValueInWithdrawal` understates the actual ETH value of the converter's holdings → `_getTotalEthInProtocol()` returns a lower value than actual → rsETH price is understated → new depositors receive more rsETH than they are entitled to → existing rsETH holders are diluted (**theft of yield from existing holders**).
- **LST price decreases during unstaking:** `ethValueInWithdrawal` overstates the actual ETH value → rsETH price is overstated → new depositors receive fewer rsETH than they are entitled to → existing holders benefit at the expense of new depositors (**contract fails to deliver promised returns**).

The magnitude scales with the size of the converter's LST holdings and the duration of the unstaking window (Lido's withdrawal queue can take days to weeks).

### Likelihood Explanation

`transferAssetFromDepositPool` is a routine operational call used to move LSTs into the converter for unstaking. The Lido withdrawal queue routinely takes multiple days. LST/ETH exchange rates are not static — stETH, ETHx, rETH, and sfrxETH all accrue staking rewards continuously, causing their ETH price to drift upward over time. A price drift of even 0.1% over a multi-day unstaking window on a large converter balance produces a measurable mis-accounting in the rsETH price. This is a normal operating condition, not an edge case.

### Recommendation

Track the raw LST token amount held in the converter (per asset) rather than a stale ETH-value snapshot. When `_getTotalEthInProtocol()` needs the ETH value of converter holdings, compute it dynamically using the current oracle price:

```solidity
// Instead of:
ethValueInWithdrawal += (_amount * lrtOracle.getAssetPrice(_asset)) / 1e18;

// Track:
lstAmountInConverter[_asset] += _amount;

// And compute dynamically in getETHDistributionData():
ethLyingInConverter = lstAmountInConverter[stETH] * currentStETHPrice / 1e18 + ...;
```

### Proof of Concept

1. Protocol holds 10,000 stETH in the converter. stETH price at transfer time = 1.05 ETH.
   - `ethValueInWithdrawal = 10,500 ETH` (snapshot)
   - stETH is removed from stETH accounting (`assetLyingInConverter = 0`)

2. Over the next 7 days (Lido withdrawal queue), stETH accrues rewards; price rises to 1.06 ETH.
   - Actual ETH value of converter holdings = 10,600 ETH
   - `ethValueInWithdrawal` still = 10,500 ETH (stale)

3. `updateRSETHPrice()` is called. `_getTotalEthInProtocol()` uses the stale 10,500 ETH instead of 10,600 ETH.
   - rsETH price is understated by 100 ETH / rsethSupply.
   - With 100,000 rsETH in supply: price understated by ~0.001 ETH/rsETH (0.1%).

4. A new depositor calls `depositETH(1000 ETH)`. They receive `1000 / understated_price` rsETH — more than fair value — diluting all existing holders by the 100 ETH discrepancy. [7](#0-6) [8](#0-7) [9](#0-8)

### Citations

**File:** contracts/LRTConverter.sol (L128-143)
```text
    function transferAssetFromDepositPool(
        address _asset,
        uint256 _amount
    )
        external
        onlySupportedERC20Token(_asset)
        onlyAssetTransferRole
    {
        address lrtDepositPoolAddress = lrtConfig.getContract(LRTConstants.LRT_DEPOSIT_POOL);
        address lrtOracleAddress = lrtConfig.getContract(LRTConstants.LRT_ORACLE);
        ILRTOracle lrtOracle = ILRTOracle(lrtOracleAddress);

        ethValueInWithdrawal += (_amount * lrtOracle.getAssetPrice(_asset)) / 1e18;

        IERC20(_asset).safeTransferFrom(lrtDepositPoolAddress, address(this), _amount);
    }
```

**File:** contracts/LRTConverter.sol (L157-165)
```text
        address lrtDepositPoolAddress = lrtConfig.getContract(LRTConstants.LRT_DEPOSIT_POOL);
        address lrtOracleAddress = lrtConfig.getContract(LRTConstants.LRT_ORACLE);
        ILRTOracle lrtOracle = ILRTOracle(lrtOracleAddress);
        uint256 assetValue = (_amount * lrtOracle.getAssetPrice(_asset)) / 1e18;

        // Set to 0 if assetValue exceeds ethValueInWithdrawal, otherwise subtract assetValue
        ethValueInWithdrawal = ethValueInWithdrawal > assetValue ? ethValueInWithdrawal - assetValue : 0;

        IERC20(_asset).safeTransfer(lrtDepositPoolAddress, _amount);
```

**File:** contracts/LRTDepositPool.sol (L385-397)
```text
    function getTotalAssetDeposits(address asset) public view override returns (uint256 totalAssetDeposit) {
        (
            uint256 assetLyingInDepositPool,
            uint256 assetLyingInNDCs,
            uint256 assetStakedInEigenLayer,
            uint256 assetUnstakingFromEigenLayer,
            uint256 assetLyingInConverter,
            uint256 assetLyingUnstakingVault
        ) = getAssetDistributionData(asset);
        uint256 effectiveAssetWithEigenLayer = assetStakedInEigenLayer + assetUnstakingFromEigenLayer;
        return (assetLyingInDepositPool + assetLyingInNDCs + effectiveAssetWithEigenLayer + assetLyingInConverter
                + assetLyingUnstakingVault);
    }
```

**File:** contracts/LRTDepositPool.sol (L458-461)
```text
        address lrtUnstakingVault = lrtConfig.getContract(LRTConstants.LRT_UNSTAKING_VAULT);

        assetLyingInConverter = 0; // assets in converter are accounted in their eth value => getETHDistributionData()
        assetLyingUnstakingVault = IERC20(asset).balanceOf(lrtUnstakingVault);
```

**File:** contracts/LRTDepositPool.sol (L498-499)
```text
        address lrtConverter = lrtConfig.getContract(LRTConstants.LRT_CONVERTER);
        ethLyingInConverter = ILRTConverter(lrtConverter).ethValueInWithdrawal();
```

**File:** contracts/LRTOracle.sol (L249-250)
```text
        // compute new rsETH price based on total ETH minus fee
        uint256 newRsETHPrice = (totalETHInProtocol - protocolFeeInETH).divWad(rsethSupply);
```

**File:** contracts/LRTOracle.sol (L331-349)
```text
    function _getTotalEthInProtocol() private view returns (uint256 totalETHInProtocol) {
        address lrtDepositPoolAddr = lrtConfig.getContract(LRTConstants.LRT_DEPOSIT_POOL);
        address[] memory supportedAssets = lrtConfig.getSupportedAssetList();
        uint256 supportedAssetCount = supportedAssets.length;

        for (uint16 assetIdx; assetIdx < supportedAssetCount;) {
            address asset = supportedAssets[assetIdx];
            // assetER is in 1e18 precision (1.0 = 1e18)
            uint256 assetER = getAssetPrice(asset);
            // totalAssetAmt is in 1e18 precision (standard token decimals)
            uint256 totalAssetAmt = ILRTDepositPool(lrtDepositPoolAddr).getTotalAssetDeposits(asset);

            totalETHInProtocol += totalAssetAmt.mulWad(assetER);

            unchecked {
                ++assetIdx;
            }
        }
    }
```
