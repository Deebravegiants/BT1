### Title
First-Depositor rsETH Price Inflation via Unrestricted ETH Donation to LRTDepositPool - (File: contracts/LRTDepositPool.sol)

### Summary
An attacker can be the first depositor, then donate ETH directly to `LRTDepositPool` via its unrestricted `receive()` function. When `updateRSETHPrice()` is subsequently called, the stored `rsETHPrice` is inflated to an extreme value. Subsequent depositors who pass `minRSETHAmountExpected = 0` receive zero rsETH, losing their deposited ETH entirely to the attacker.

### Finding Description

The rsETH minting formula in `LRTDepositPool.getRsETHAmountToMint()` is:

```
rsethAmountToMint = (amount * lrtOracle.getAssetPrice(asset)) / lrtOracle.rsETHPrice()
``` [1](#0-0) 

The stored `rsETHPrice` is computed in `LRTOracle._updateRsETHPrice()` as:

```
newRsETHPrice = totalETHInProtocol / rsethSupply
``` [2](#0-1) 

`totalETHInProtocol` is derived from `_getTotalEthInProtocol()`, which calls `getTotalAssetDeposits()` for each supported asset. For ETH, this resolves to `getETHDistributionData()`, which reads `address(this).balance` directly: [3](#0-2) 

`LRTDepositPool` has a completely unrestricted `receive()` function: [4](#0-3) 

This means any ETH sent directly to the contract is immediately counted as protocol TVL without minting any rsETH. The same applies to ERC20 LST assets: `getAssetDistributionData()` reads `IERC20(asset).balanceOf(address(this))` directly, so a direct ERC20 transfer also inflates TVL. [5](#0-4) 

The price-increase guard in `_updateRsETHPrice()` only activates when `pricePercentageLimit > 0`. This variable defaults to `0` and must be explicitly configured by an admin: [6](#0-5) 

When `pricePercentageLimit == 0`, the guard is entirely bypassed, allowing an unbounded price increase.

### Impact Explanation

**Critical — Direct theft of user funds.**

Attack steps:
1. Attacker calls `depositETH(0, "")` with `msg.value = minAmountToDeposit`. They receive a small amount of rsETH (the entire supply).
2. Attacker sends `D` ETH directly to `LRTDepositPool` via `receive()`. No rsETH is minted.
3. Attacker calls `LRTOracle.updateRSETHPrice()` (public, permissionless). The new price becomes approximately `D * 1e18 / rsethSupply`, an extreme value.
4. Victim calls `depositETH(0, "")` with `msg.value = V` ETH (where `V < D`). The computed `rsethAmountToMint = V * 1e18 / (D * 1e18) = V/D < 1`, which truncates to **0**. The victim's ETH is accepted into the pool but they receive zero rsETH.
5. Attacker requests withdrawal of their rsETH (100% of supply) and recovers all ETH in the pool: their donation `D` + initial deposit + victim's `V` ETH.

Net attacker profit: `V` ETH (victim's deposit). The donated `D` ETH is fully recovered on redemption.

The `_beforeDeposit` check only reverts if `rsethAmountToMint < minRSETHAmountExpected`: [7](#0-6) 

When the victim passes `minRSETHAmountExpected = 0` (a valid input), the zero-rsETH deposit is silently accepted and the victim's funds are permanently lost.

### Likelihood Explanation

**Low.** The attack requires:
1. `pricePercentageLimit` is unconfigured (= 0), which is the default state.
2. The victim passes `minRSETHAmountExpected = 0` — possible via direct contract calls or integrations that omit slippage protection.
3. The attacker must front-run the victim's deposit and lock up `D ≈ V` ETH for the EigenLayer withdrawal delay period.
4. The attack is most dangerous at protocol launch before `pricePercentageLimit` is set.

The economic cost (locking `D` ETH for the withdrawal delay) limits opportunistic exploitation, but a targeted griefing or theft of a large deposit remains feasible.

### Recommendation

1. **Remove the unrestricted `receive()` function** or track ETH balance via an internal accounting variable (incremented only on legitimate deposits), rather than using `address(this).balance` directly in TVL calculations.
2. **Enforce a non-zero `minRSETHAmountExpected`** at the protocol level (e.g., revert if `rsethAmountToMint == 0`).
3. **Ensure `pricePercentageLimit` is set before the first deposit** as part of the deployment checklist.
4. Consider minting a small amount of rsETH to a dead address at initialization (analogous to Uniswap V2's minimum liquidity lock) to prevent the total supply from ever being 1 wei.

### Proof of Concept

```solidity
// Precondition: pricePercentageLimit == 0 (default)
// Precondition: minAmountToDeposit == 0 or small

// Step 1: Attacker becomes first depositor
lrtDepositPool.depositETH{value: 1 wei}(0, "attacker");
// rsETH supply = 1 wei, rsETHPrice = 1e18

// Step 2: Attacker donates 1000 ETH directly (no rsETH minted)
(bool ok,) = address(lrtDepositPool).call{value: 1000 ether}("");

// Step 3: Inflate the stored price
lrtOracle.updateRSETHPrice();
// newRsETHPrice ≈ 1000e18 * 1e18 / 1 = 1e39

// Step 4: Victim deposits 1 ETH with no slippage protection
// rsethAmountToMint = 1e18 * 1e18 / 1e39 = 0 → victim gets 0 rsETH
lrtDepositPool.depositETH{value: 1 ether}(0, "victim"); // victim loses 1 ETH

// Step 5: Attacker redeems 1 wei rsETH (100% of supply)
// Recovers: 1000 ETH (donation) + 1 wei (initial) + 1 ETH (victim) = ~1001 ETH
// Net profit: ~1 ETH (victim's deposit)
``` [8](#0-7) [9](#0-8) [10](#0-9)

### Citations

**File:** contracts/LRTDepositPool.sol (L58-58)
```text
    receive() external payable { }
```

**File:** contracts/LRTDepositPool.sol (L76-93)
```text
    function depositETH(
        uint256 minRSETHAmountExpected,
        string calldata referralId
    )
        external
        payable
        nonReentrant
        whenNotPaused
        onlySupportedAsset(LRTConstants.ETH_TOKEN)
    {
        // checks
        uint256 rsethAmountToMint = _beforeDeposit(LRTConstants.ETH_TOKEN, msg.value, minRSETHAmountExpected);

        // interactions
        _mintRsETH(rsethAmountToMint);

        emit ETHDeposit(msg.sender, msg.value, rsethAmountToMint, referralId);
    }
```

**File:** contracts/LRTDepositPool.sol (L444-444)
```text
        assetLyingInDepositPool = IERC20(asset).balanceOf(address(this));
```

**File:** contracts/LRTDepositPool.sol (L480-480)
```text
        ethLyingInDepositPool = address(this).balance;
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

**File:** contracts/LRTDepositPool.sol (L665-669)
```text
        rsethAmountToMint = getRsETHAmountToMint(asset, depositAmount);

        if (rsethAmountToMint < minRSETHAmountExpected) {
            revert MinimumAmountToReceiveNotMet();
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

**File:** contracts/LRTOracle.sol (L329-349)
```text
    /// @notice get total ETH in protocol
    /// @return totalETHInProtocol total ETH in protocol (normalized to 1e18)
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
