### Title
Stale Cached `rsETHPrice` Allows Depositors to Mint Excess rsETH, Stealing Accrued Yield from Existing Holders - (`contracts/LRTDepositPool.sol`)

---

### Summary

`LRTDepositPool.getRsETHAmountToMint()` uses `lrtOracle.rsETHPrice()`, which is a **cached/stored** value in `LRTOracle` that must be manually updated via `updateRSETHPrice()`. Between updates, this stored price can be stale (lower than the true current value reflecting accrued staking rewards). A depositor who deposits ETH or LSTs while the price is stale receives more rsETH than they deserve, effectively stealing the accrued yield from existing rsETH holders.

---

### Finding Description

`LRTOracle` stores `rsETHPrice` as a persistent state variable: [1](#0-0) 

This value is only updated when `updateRSETHPrice()` is explicitly called: [2](#0-1) 

`LRTDepositPool.getRsETHAmountToMint()` divides by this cached price to determine how many rsETH tokens to mint: [3](#0-2) 

Neither `depositETH()` nor `depositAsset()` calls `updateRSETHPrice()` before computing the mint amount: [4](#0-3) 

When staking rewards accrue (e.g., EigenLayer restaking yields, LST appreciation), the true rsETH price rises above the stored `rsETHPrice`. Because the formula is:

```
rsETHMinted = depositAmount * assetPrice / rsETHPrice
```

a stale (lower) `rsETHPrice` causes the numerator to be divided by a smaller denominator, minting **more rsETH than deserved**. This dilutes existing holders by distributing their accrued yield to the new depositor.

A concrete staleness window is guaranteed when `pricePercentageLimit` is set and the true price increase exceeds it — in that case, `updateRSETHPrice()` reverts for non-managers: [5](#0-4) 

During this window, the price is stuck at the stale value and only a manager can advance it, creating a guaranteed multi-block window for exploitation.

---

### Impact Explanation

**High — Theft of unclaimed yield.**

Existing rsETH holders have accrued yield (reflected in the true rsETH/ETH rate being higher than the stored `rsETHPrice`). A depositor who deposits before `updateRSETHPrice()` is called receives more rsETH than the true rate warrants. When the price is eventually updated, the total rsETH supply is inflated, permanently diluting existing holders. The attacker can sell the excess rsETH on secondary markets at the true (higher) price, capturing the yield that belonged to existing holders.

The magnitude scales with:
- The staleness duration (longer gap between `updateRSETHPrice()` calls → more accrued yield)
- The deposit size (larger deposit → larger share of the stolen yield)
- The `pricePercentageLimit` scenario (guaranteed multi-block staleness window)

---

### Likelihood Explanation

**Moderate-to-High.** Staking rewards accrue continuously. Any gap between `updateRSETHPrice()` calls creates a window. While `updateRSETHPrice()` is public and callable by anyone, MEV bots and arbitrageurs have an incentive to **not** call it before depositing (to exploit the stale price). The `pricePercentageLimit` guard creates a guaranteed staleness window whenever the true price increase exceeds the configured threshold, since only managers can advance the price in that case. [6](#0-5) 

---

### Recommendation

Call `updateRSETHPrice()` (or inline the price computation) at the beginning of `depositETH()` and `depositAsset()` before computing `rsethAmountToMint`, analogous to the mitigation in the reference report:

```solidity
function depositETH(uint256 minRSETHAmountExpected, string calldata referralId)
    external payable nonReentrant whenNotPaused onlySupportedAsset(LRTConstants.ETH_TOKEN)
{
+   ILRTOracle(lrtConfig.getContract(LRTConstants.LRT_ORACLE)).updateRSETHPrice();
    uint256 rsethAmountToMint = _beforeDeposit(LRTConstants.ETH_TOKEN, msg.value, minRSETHAmountExpected);
    _mintRsETH(rsethAmountToMint);
    emit ETHDeposit(msg.sender, msg.value, rsethAmountToMint, referralId);
}
```

Apply the same fix to `depositAsset()`. This ensures the rsETH price always reflects the current accrued yield before any new shares are minted.

---

### Proof of Concept

1. Staking rewards accrue in EigenLayer over time. True rsETH price rises from `P_stale` to `P_true` (e.g., `P_stale = 1.00 ETH`, `P_true = 1.05 ETH`). `updateRSETHPrice()` has not been called.
2. Attacker calls `depositETH{value: 100 ETH}(minRSETHAmountExpected, "")`.
3. `getRsETHAmountToMint` computes: `100e18 * 1e18 / P_stale = 100 rsETH` instead of the correct `100e18 * 1e18 / P_true ≈ 95.24 rsETH`.
4. Attacker receives `~4.76 rsETH` in excess.
5. Attacker sells the excess rsETH on a secondary market at `P_true`, capturing `~4.76 * 1.05 ≈ 5 ETH` of yield that belonged to existing holders.
6. When `updateRSETHPrice()` is eventually called, the inflated supply permanently dilutes existing holders. [7](#0-6) [8](#0-7)

### Citations

**File:** contracts/LRTOracle.sol (L28-28)
```text
    uint256 public override rsETHPrice;
```

**File:** contracts/LRTOracle.sol (L87-89)
```text
    function updateRSETHPrice() public whenNotPaused {
        _updateRsETHPrice();
    }
```

**File:** contracts/LRTOracle.sol (L214-250)
```text
    function _updateRsETHPrice() internal {
        address rsETHTokenAddress = lrtConfig.rsETH();
        uint256 rsethSupply = IRSETH(rsETHTokenAddress).totalSupply();

        if (rsethSupply == 0) {
            rsETHPrice = 1 ether;
            highestRsethPrice = 1 ether;
            return;
        }

        if (highestRsethPrice == 0) {
            highestRsethPrice = rsETHPrice;
        }

        uint256 previousPrice = rsETHPrice;

        // get total ETH in the protocol (normalized to 1e18)
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

        // compute new rsETH price based on total ETH minus fee
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
