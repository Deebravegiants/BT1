### Title
Deposits Mint rsETH Using Stale Cached `rsETHPrice` Without Prior Oracle Update, Enabling Yield Extraction From Existing Holders - (File: contracts/LRTDepositPool.sol)

### Summary
`LRTDepositPool.depositETH` and `depositAsset` calculate the rsETH amount to mint using `lrtOracle.rsETHPrice()`, which is a **stored/cached** state variable that is only updated when `updateRSETHPrice()` is explicitly called. No price update is triggered before the deposit calculation. When staking rewards accrue and increase the protocol's TVL, the stored `rsETHPrice` becomes stale (lower than the true current price), causing depositors to receive more rsETH than their deposit is worth, extracting accrued yield from existing holders.

### Finding Description
`LRTDepositPool.getRsETHAmountToMint` computes the rsETH to mint as:

```solidity
rsethAmountToMint = (amount * lrtOracle.getAssetPrice(asset)) / lrtOracle.rsETHPrice();
```

`lrtOracle.getAssetPrice(asset)` is a live external oracle call, but `lrtOracle.rsETHPrice()` reads the **stored** state variable `rsETHPrice` in `LRTOracle`, which is only updated when `_updateRsETHPrice()` is invoked. [1](#0-0) 

`rsETHPrice` is a plain storage variable set at the end of `_updateRsETHPrice()`: [2](#0-1) [3](#0-2) 

Neither `depositETH` nor `depositAsset` calls `updateRSETHPrice()` before computing the mint amount: [4](#0-3) [5](#0-4) 

The `_beforeDeposit` helper performs the limit check and mint calculation entirely with the stale price: [5](#0-4) 

Additionally, `updateRSETHPrice()` is gated by `pricePercentageLimit`: if the true price has risen beyond the configured threshold, the public `updateRSETHPrice()` reverts for non-managers, meaning the stale price can persist for an extended period while deposits continue at the outdated rate: [6](#0-5) 

### Impact Explanation
When staking rewards accrue and increase `totalETHInProtocol`, the true rsETH price rises above the stored `rsETHPrice`. A depositor who deposits `A` ETH at the stale price `P_stale < P_actual` receives:

```
rsETH_minted = A / P_stale  >  A / P_actual  (correct amount)
```

The excess rsETH represents a larger ownership share of the protocol than the deposit warrants. After `updateRSETHPrice()` is called and the price corrects upward, the attacker's rsETH is worth more than they deposited. The difference is extracted from the yield that had accrued to existing holders — their proportional share of the protocol is diluted. This is **theft of unclaimed yield** (High severity).

### Likelihood Explanation
`updateRSETHPrice()` is a public function with no access restriction, callable by anyone. Rewards accrue continuously from EigenLayer restaking. Any period between oracle updates — which can be extended when `pricePercentageLimit` causes the public update to revert — creates an exploitable window. An attacker can:
1. Monitor the on-chain `rsETHPrice` vs. the computed TVL to detect staleness.
2. Deposit at the stale price.
3. Call `updateRSETHPrice()` (or wait for the manager to call `updateRSETHPriceAsManager()`).
4. Redeem at the corrected price for a profit.

No privileged access is required. The attack is straightforward and repeatable.

### Recommendation
Call `updateRSETHPrice()` (or an internal equivalent) at the beginning of `depositETH` and `depositAsset` — or inside `_beforeDeposit` — before computing `rsethAmountToMint`. This mirrors the fix recommended in H-01: accrue all state changes before performing any dependent checks or calculations.

```solidity
function _beforeDeposit(address asset, uint256 depositAmount, uint256 minRSETHAmountExpected)
    private
    returns (uint256 rsethAmountToMint)
{
    // Update rsETH price first, so mint calculation uses current price
    ILRTOracle(lrtConfig.getContract(LRTConstants.LRT_ORACLE)).updateRSETHPrice();

    if (depositAmount == 0 || depositAmount < minAmountToDeposit) revert InvalidAmountToDeposit();
    if (_checkIfDepositAmountExceedesCurrentLimit(asset, depositAmount)) revert MaximumDepositLimitReached();

    rsethAmountToMint = getRsETHAmountToMint(asset, depositAmount);
    if (rsethAmountToMint < minRSETHAmountExpected) revert MinimumAmountToReceiveNotMet();
}
```

### Proof of Concept
1. At `t=0`: `rsETHPrice = 1.00 ETH`, total ETH in protocol = 1000 ETH, rsETH supply = 1000.
2. At `t=1`: Staking rewards add 10 ETH. True price = 1010/1000 = 1.01 ETH. `rsETHPrice` is still `1.00` (not updated).
3. Attacker calls `depositETH{value: 100 ETH}`.
   - `rsethAmountToMint = 100 / 1.00 = 100 rsETH` (should be `100 / 1.01 ≈ 99.01 rsETH`).
4. Attacker calls `updateRSETHPrice()`.
   - New supply = 1100 rsETH, new TVL = 1110 ETH.
   - `rsETHPrice = 1110 / 1100 ≈ 1.009 ETH`.
5. Attacker holds 100 rsETH worth `100 × 1.009 = 100.9 ETH` — deposited 100 ETH, extracted ~0.9 ETH of yield from existing holders. [7](#0-6) [8](#0-7) [9](#0-8)

### Citations

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

**File:** contracts/LRTDepositPool.sol (L648-670)
```text
    function _beforeDeposit(
        address asset,
        uint256 depositAmount,
        uint256 minRSETHAmountExpected
    )
        private
        view
        returns (uint256 rsethAmountToMint)
    {
        if (depositAmount == 0 || depositAmount < minAmountToDeposit) {
            revert InvalidAmountToDeposit();
        }

        if (_checkIfDepositAmountExceedesCurrentLimit(asset, depositAmount)) {
            revert MaximumDepositLimitReached();
        }

        rsethAmountToMint = getRsETHAmountToMint(asset, depositAmount);

        if (rsethAmountToMint < minRSETHAmountExpected) {
            revert MinimumAmountToReceiveNotMet();
        }
    }
```

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

**File:** contracts/LRTOracle.sol (L313-313)
```text
        rsETHPrice = newRsETHPrice;
```
