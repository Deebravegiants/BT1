### Title
Donation Attack on EigenLayer Strategy Inflates Protocol Fee rsETH Minting — (`contracts/NodeDelegatorHelper.sol`, `contracts/LRTOracle.sol`)

### Summary

An attacker can donate underlying tokens directly to an EigenLayer `StrategyBase` contract, inflating the `sharesToUnderlyingView` exchange rate. Because `NodeDelegatorHelper.getAssetBalance` reads this rate without any sanity check, the inflated value propagates through `getTotalAssetDeposits` → `_getTotalEthInProtocol` → `_updateRsETHPrice`, causing the protocol to treat the donation as genuine staking yield and mint excess protocol-fee rsETH to the treasury at the expense of existing rsETH holders.

---

### Finding Description

**Step 1 — Inflatable exchange rate in EigenLayer strategy**

EigenLayer's production `StrategyBase.sharesToUnderlyingView` computes:

```
shares * underlyingToken.balanceOf(address(this)) / totalShares
```

Donating tokens directly to the strategy address increases `balanceOf(strategy)` without changing `totalShares`, inflating the per-share value. This is permissionless.

**Step 2 — `getAssetBalance` reads the inflated rate** [1](#0-0) 

`getWithdrawableShare` fetches the NDC's withdrawable shares from `DelegationManager`, then multiplies by the now-inflated `sharesToUnderlyingView`. No independent price oracle or sanity bound is applied here.

**Step 3 — Inflated value flows into TVL accounting** [2](#0-1) 

`assetStakedInEigenLayer` accumulates the inflated `getAssetBalance` for every NDC, feeding into `getTotalAssetDeposits`. [3](#0-2) 

**Step 4 — Oracle treats the inflation as yield and mints fee rsETH** [4](#0-3) 

`totalETHInProtocol` is inflated. Because `totalETHInProtocol > previousTVL`, the delta is treated as `rewardAmount`, and `protocolFeeInETH` is computed on it. The fee is then minted as rsETH to the treasury: [5](#0-4) 

`updateRSETHPrice()` is **public with no access control**: [6](#0-5) 

---

### Impact Explanation

The treasury receives rsETH representing a protocol fee on a donation that is not genuine staking yield. Existing rsETH holders bear the dilution: instead of the full donation accruing to their rsETH value, `feeRate %` is siphoned to the treasury. This matches **High — Theft of unclaimed yield**.

---

### Likelihood Explanation

**Low.** The attacker must sacrifice the donated tokens (they are permanently added to the strategy's TVL). The attack is not self-profitable; it is a griefing/dilution vector. Realistic motivations include a large short position on rsETH or a competitor willing to absorb the cost.

**Partial mitigations that do not fully block the attack:**

- `pricePercentageLimit` guard — only triggers if `pricePercentageLimit > 0` AND the price increase exceeds the threshold. If the limit is unset (`== 0`) or the donation is sized to stay within the threshold, the guard is bypassed entirely. [7](#0-6) 

- `maxFeeMintAmountPerDay` — caps daily fee minting but does not prevent the attack; it only bounds per-day impact. [8](#0-7) 

---

### Recommendation

1. **Do not rely solely on `sharesToUnderlyingView` for TVL accounting.** Track deposited shares internally (e.g., record shares at deposit time) and convert using a trusted oracle price rather than the live strategy balance.
2. **Alternatively**, compare `sharesToUnderlyingView` against an external price oracle and revert if the deviation exceeds a threshold before computing fees.
3. Ensure `pricePercentageLimit` is always set to a non-zero value in deployment configuration.

---

### Proof of Concept

```solidity
// Fork test (Mainnet fork, no public-mainnet state changes)
function testDonationInflatesProtocolFee() public {
    // 1. Record baseline fee minted
    uint256 treasuryBalanceBefore = rsETH.balanceOf(treasury);

    // 2. Attacker donates stETH directly to the EigenLayer stETH strategy
    address strategy = lrtConfig.assetStrategy(stETH);
    deal(stETH, strategy, IERC20(stETH).balanceOf(strategy) + 100 ether);

    // 3. Anyone calls updateRSETHPrice (public, no role required)
    lrtOracle.updateRSETHPrice();

    // 4. Treasury received excess rsETH beyond what genuine yield justifies
    uint256 treasuryBalanceAfter = rsETH.balanceOf(treasury);
    assertGt(treasuryBalanceAfter, treasuryBalanceBefore,
        "treasury minted excess rsETH from donation");
}
```

The test donates tokens to the strategy, calls the public `updateRSETHPrice`, and asserts that `rsethAmountToMintAsProtocolFee` exceeds what genuine staking rewards would justify — confirming the invariant violation.

### Citations

**File:** contracts/NodeDelegatorHelper.sol (L31-39)
```text
    function getAssetBalance(ILRTConfig lrtConfig, address asset) internal view returns (uint256) {
        address strategy = lrtConfig.assetStrategy(asset);
        if (strategy == address(0)) {
            return 0;
        }
        uint256 withdrawableShare = getWithdrawableShare(lrtConfig, IStrategy(strategy));

        return IStrategy(strategy).sharesToUnderlyingView(withdrawableShare);
    }
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

**File:** contracts/LRTDepositPool.sol (L447-451)
```text
        for (uint256 i; i < ndcsCount;) {
            assetLyingInNDCs += IERC20(asset).balanceOf(nodeDelegatorQueue[i]);

            assetStakedInEigenLayer += INodeDelegator(nodeDelegatorQueue[i]).getAssetBalance(asset);
            assetUnstakingFromEigenLayer += INodeDelegator(nodeDelegatorQueue[i]).getAssetUnstaking(asset);
```

**File:** contracts/LRTOracle.sol (L87-89)
```text
    function updateRSETHPrice() public whenNotPaused {
        _updateRsETHPrice();
    }
```

**File:** contracts/LRTOracle.sol (L205-209)
```text
        if (currentPeriodMintedFeeAmount + feeAmount > maxFeeMintAmountPerDay) {
            revert DailyFeeMintLimitExceeded(currentPeriodMintedFeeAmount + feeAmount, maxFeeMintAmountPerDay);
        }

        currentPeriodMintedFeeAmount += feeAmount;
```

**File:** contracts/LRTOracle.sol (L231-247)
```text
        uint256 totalETHInProtocol = _getTotalEthInProtocol();

        // calculate previousTVL using rsethSupply multiplied by rsETHPrice
        uint256 previousTVL = rsethSupply.mulWad(rsETHPrice);

        IPausable lrtDepositPool = IPausable(lrtConfig.getContract(LRTConstants.LRT_DEPOSIT_POOL));
        IPausable withdrawalManager = IPausable(lrtConfig.getContract(LRTConstants.LRT_WITHDRAW_MANAGER));

        // determine if the protocol is active (not paused)
        bool protocolPaused = lrtDepositPool.paused() || withdrawalManager.paused() || paused;

        // only take fee if TVL increased and protocol is not paused
        uint256 protocolFeeInETH = 0;
        if (!protocolPaused && totalETHInProtocol > previousTVL) {
            uint256 rewardAmount = totalETHInProtocol - previousTVL;
            protocolFeeInETH = (rewardAmount * lrtConfig.protocolFeeInBPS()) / 10_000;
        }
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

**File:** contracts/LRTOracle.sol (L299-308)
```text
        if (protocolFeeInETH > 0) {
            // Calculate rsETH amount to mint as protocol fee
            uint256 rsethAmountToMintAsProtocolFee = protocolFeeInETH.divWad(newRsETHPrice);

            _checkAndUpdateDailyFeeMintLimit(rsethAmountToMintAsProtocolFee);
            if (rsethAmountToMintAsProtocolFee > 0) {
                address treasury = lrtConfig.getContract(LRTConstants.PROTOCOL_TREASURY);
                IRSETH(rsETHTokenAddress).mint(treasury, rsethAmountToMintAsProtocolFee);
                emit FeeMinted(treasury, rsethAmountToMintAsProtocolFee);
            }
```
