### Title
Share Inflation Attack via `rsETHPrice` Manipulation on First Deposit - (File: `contracts/LRTOracle.sol`, `contracts/LRTDepositPool.sol`)

---

### Summary

The `rsETHPrice` stored in `LRTOracle` is computed as `totalETHInProtocol / rsethSupply`. Because `totalETHInProtocol` reads live `balanceOf` values from `LRTDepositPool` (including direct token donations), and `updateRSETHPrice()` is a public, permissionless function with no price-increase guard when `pricePercentageLimit == 0` (the default), an attacker can inflate `rsETHPrice` to an arbitrarily large value when `rsethSupply` is tiny. Subsequent depositors receive 0 rsETH (their deposit rounds down to zero), while the attacker's 1-wei rsETH position represents the entire protocol TVL.

---

### Finding Description

**Root cause — `LRTOracle._updateRsETHPrice()`:** [1](#0-0) 

When `rsethSupply > 0`, the new price is:

```solidity
uint256 newRsETHPrice = (totalETHInProtocol - protocolFeeInETH).divWad(rsethSupply);
``` [2](#0-1) 

`totalETHInProtocol` is computed by `_getTotalEthInProtocol()`, which calls `ILRTDepositPool.getTotalAssetDeposits(asset)` for every supported asset. [3](#0-2) 

`getTotalAssetDeposits` ultimately reads `IERC20(asset).balanceOf(address(this))` for the DepositPool — meaning a direct ERC20 transfer to the DepositPool inflates the TVL figure. [4](#0-3) 

**Root cause — `updateRSETHPrice()` is public with no access control:** [5](#0-4) 

**Root cause — price-increase guard is disabled when `pricePercentageLimit == 0` (default):** [6](#0-5) 

`pricePercentageLimit` is never set in `initialize()`, so it defaults to `0`, making `isPriceIncreaseOffLimit` always `false`.

**Root cause — minting uses the stored (manipulable) `rsETHPrice`:** [7](#0-6) 

```solidity
rsethAmountToMint = (amount * lrtOracle.getAssetPrice(asset)) / lrtOracle.rsETHPrice();
```

If `rsETHPrice` is inflated to `X`, a victim depositing `amount` receives `amount * assetPrice / X`, which rounds down to 0 when `X >> amount * assetPrice`.

---

### Impact Explanation

**Critical — Direct theft of user funds.**

The victim deposits a large amount of LST/ETH and receives 0 rsETH. Their assets are permanently absorbed into the protocol TVL. The attacker's 1-wei rsETH position represents 100% of the rsETH supply and therefore 100% of the TVL (including the victim's deposit). When the attacker initiates withdrawal, they redeem their 1-wei rsETH at the inflated price and extract the victim's funds.

The attack is repeatable: after each victim deposit, the attacker can repeat the cycle to steal every subsequent depositor's funds.

---

### Likelihood Explanation

**Medium-to-High.** The attack requires:
1. Being the first depositor (or acting when `rsethSupply` is near zero after a protocol reset).
2. Holding enough LST to donate (the donation amount must exceed the victim's deposit to force rounding to zero).
3. Calling the public `updateRSETHPrice()` — no privilege required.

The attack is front-runnable: the attacker watches the mempool for the first legitimate deposit, front-runs with steps 1–3, and back-runs with the withdrawal. The only natural mitigation (`pricePercentageLimit`) is unset by default.

---

### Recommendation

1. **Set `pricePercentageLimit` to a non-zero value at initialization** (e.g., 1% = `1e16`) so that a sudden price spike from a donation triggers a revert for non-manager callers.
2. **Seed the protocol with a non-trivial initial rsETH mint to `address(0)`** on first deployment, analogous to the fix in the referenced report, so `rsethSupply` is never 1 wei.
3. **Snapshot TVL at deposit time** rather than reading live `balanceOf`, or use a time-weighted price to prevent single-block manipulation.
4. **Add a minimum rsETH output check** (already partially present via `minRSETHAmountExpected`) and enforce it is always non-zero.

---

### Proof of Concept

```
Initial state:
  rsETHPrice = 1e18 (set by updateRSETHPrice() when rsethSupply == 0)
  rsethSupply = 0

Step 1 — Attacker deposits 1 wei stETH:
  rsethAmountToMint = (1 * 1e18) / 1e18 = 1 wei rsETH
  rsethSupply = 1

Step 2 — Attacker directly transfers 1,000,000e18 stETH to LRTDepositPool:
  LRTDepositPool.balanceOf(stETH) = 1,000,000e18 + 1

Step 3 — Attacker calls updateRSETHPrice() (public, no access control):
  totalETHInProtocol ≈ 1,000,000e18 * 1e18 / 1e18 = 1,000,000e18
  newRsETHPrice = 1,000,000e18 * 1e18 / 1 = 1,000,000e36
  pricePercentageLimit == 0 → isPriceIncreaseOffLimit = false → no revert
  rsETHPrice = 1,000,000e36

Step 4 — Victim deposits 1,000,000e18 stETH:
  rsethAmountToMint = (1,000,000e18 * 1e18) / 1,000,000e36
                    = 1,000,000e36 / 1,000,000e36 < 1
                    → rounds down to 0
  Victim receives 0 rsETH. Funds absorbed into TVL.

Step 5 — Attacker redeems 1 wei rsETH (= 100% of supply):
  Entitled to 100% of TVL ≈ 2,000,000e18 stETH
  Attacker profit ≈ 1,000,000e18 stETH (victim's deposit)
``` [5](#0-4) [2](#0-1) [8](#0-7) [6](#0-5)

### Citations

**File:** contracts/LRTOracle.sol (L87-89)
```text
    function updateRSETHPrice() public whenNotPaused {
        _updateRsETHPrice();
    }
```

**File:** contracts/LRTOracle.sol (L214-222)
```text
    function _updateRsETHPrice() internal {
        address rsETHTokenAddress = lrtConfig.rsETH();
        uint256 rsethSupply = IRSETH(rsETHTokenAddress).totalSupply();

        if (rsethSupply == 0) {
            rsETHPrice = 1 ether;
            highestRsethPrice = 1 ether;
            return;
        }
```

**File:** contracts/LRTOracle.sol (L250-250)
```text
        uint256 newRsETHPrice = (totalETHInProtocol - protocolFeeInETH).divWad(rsethSupply);
```

**File:** contracts/LRTOracle.sol (L252-266)
```text
        if (newRsETHPrice > highestRsethPrice) {
            // check if the price is above the threshold
            uint256 priceDifference = newRsETHPrice - highestRsethPrice;
            // pricePercentageLimit is in 1e18 precision (100% = 1e18, 1% = 1e16)
            bool isPriceIncreaseOffLimit =
                pricePercentageLimit > 0 && priceDifference > pricePercentageLimit.mulWad(highestRsethPrice);

            // check if the price difference is above the threshold
            if (isPriceIncreaseOffLimit) {
                // if sender has a manager role, this doesn't revert.
                // if not, it reverts as price went above the threshold
                if (!IAccessControl(address(lrtConfig)).hasRole(LRTConstants.MANAGER, msg.sender)) {
                    revert PriceAboveDailyThreshold();
                }
            }
```

**File:** contracts/LRTOracle.sol (L331-348)
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
```

**File:** contracts/LRTDepositPool.sol (L444-444)
```text
        assetLyingInDepositPool = IERC20(asset).balanceOf(address(this));
```

**File:** contracts/LRTDepositPool.sol (L506-521)
```text
    function getRsETHAmountToMint(
        address asset,
        uint256 amount
    )
        public
        view
        override
        returns (uint256 rsethAmountToMint)
    {
        // setup oracle contract
        address lrtOracleAddress = lrtConfig.getContract(LRTConstants.LRT_ORACLE);
        ILRTOracle lrtOracle = ILRTOracle(lrtOracleAddress);

        // calculate rseth amount to mint based on asset amount and asset exchange rate
        rsethAmountToMint = (amount * lrtOracle.getAssetPrice(asset)) / lrtOracle.rsETHPrice();
    }
```
