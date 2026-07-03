### Title
Permissionless `updateRSETHPrice()` Lacks Update-Frequency Throttle, Enabling Oracle-Dip Minting Arbitrage - (File: contracts/LRTOracle.sol)

---

### Summary

`LRTOracle.updateRSETHPrice()` is a public, permissionless function with no minimum elapsed-time guard between successive calls. An unprivileged caller can invoke it at the exact moment an underlying LST oracle price is temporarily depressed, locking in a lower `rsETHPrice` storage value. Because `LRTDepositPool.getRsETHAmountToMint()` divides by the stored `rsETHPrice`, a lower stored price causes the deposit function to mint more rsETH per unit of ETH deposited. The attacker can execute both steps atomically, extracting value from existing rsETH holders through dilution.

---

### Finding Description

`updateRSETHPrice()` is declared `public whenNotPaused` with no cooldown or minimum-elapsed-time check: [1](#0-0) 

Internally, `_updateRsETHPrice()` computes the new price as:

```
newRsETHPrice = (totalETHInProtocol - protocolFeeInETH) / rsethSupply
``` [2](#0-1) 

`totalETHInProtocol` is the sum of all supported assets valued at their **current** oracle prices: [3](#0-2) 

When a supported LST oracle price (e.g., stETH/ETH) dips temporarily — within the `pricePercentageLimit` band — `newRsETHPrice` falls below `highestRsethPrice` but does **not** trigger a pause. The code simply updates `rsETHPrice` to the lower value and emits events: [4](#0-3) 

The stored `rsETHPrice` is then used as the denominator in `LRTDepositPool.getRsETHAmountToMint()`: [5](#0-4) 

When a depositor sends **ETH** (whose oracle price is always `1e18`), the numerator is unaffected by the LST dip, but the denominator (`rsETHPrice`) is depressed. The depositor therefore receives more rsETH than they would at the fair price. The excess rsETH is backed by no additional ETH, diluting all existing holders.

There is no minimum-elapsed-time variable, no `lastUpdated` cooldown check, and no per-block rate-limit anywhere in `updateRSETHPrice()` or `_updateRsETHPrice()`. [6](#0-5) 

---

### Impact Explanation

**Theft of unclaimed yield (High).**

Existing rsETH holders accumulate yield as the protocol's TVL grows relative to rsETH supply. When an attacker mints excess rsETH at a temporarily depressed `rsETHPrice`, the new rsETH is under-collateralised at the moment of minting. Once the LST oracle price recovers, `rsETHPrice` rises again, but the attacker's excess rsETH participates in that recovery. The value of the recovery that should have accrued to existing holders is instead captured by the attacker — a direct theft of yield proportional to the size of the deposit and the depth of the dip.

For a 1 % stETH/ETH dip and a 1 000 ETH deposit, the attacker mints approximately 10 extra rsETH. At a `rsETHPrice` of ~1.05 ETH, that is ~10.5 ETH extracted from existing holders.

---

### Likelihood Explanation

**Medium.**

- stETH/ETH and similar LST oracle prices fluctuate naturally by fractions of a percent on a daily basis.
- The attacker needs no special role, no flash loan, and no oracle manipulation — only a monitoring bot and a contract that calls `updateRSETHPrice()` followed by `depositETH()` atomically.
- The attack is bounded by `pricePercentageLimit`, but even a 0.5–1 % dip (well within normal market noise) is sufficient for meaningful profit at scale.
- The attack is repeatable every time a dip occurs.

---

### Recommendation

Add a minimum-elapsed-time guard to `updateRSETHPrice()`, analogous to the `minimum_elapsed_slots` pattern described in the reference report. For example:

```solidity
uint256 public minUpdateInterval; // e.g. 1 hours
uint256 public lastPriceUpdateTime;

function updateRSETHPrice() public whenNotPaused {
    require(
        block.timestamp >= lastPriceUpdateTime + minUpdateInterval,
        "UpdateTooFrequent"
    );
    lastPriceUpdateTime = block.timestamp;
    _updateRsETHPrice();
}
```

The manager-only path (`updateRSETHPriceAsManager`) should bypass this check so the protocol can respond to emergencies. The interval should be set to a value that reflects the minimum meaningful yield accrual period (e.g., 1–8 hours).

---

### Proof of Concept

```
Block N:
  stETH/ETH Chainlink price: 0.990 (natural 1 % dip)
  Current rsETHPrice (stored): 1.050 ETH  (highestRsethPrice = 1.050)
  pricePercentageLimit = 2 % → dip is within limit, no pause triggered

Attacker contract (single transaction):
  1. Call LRTOracle.updateRSETHPrice()
       totalETHInProtocol drops ~1 % due to stETH devaluation
       newRsETHPrice ≈ 1.0395 ETH  (< highestRsethPrice, within limit)
       rsETHPrice storage ← 1.0395

  2. Call LRTDepositPool.depositETH{value: 1000 ETH}(0, "")
       rsethAmountToMint = 1000e18 * 1e18 / 1.0395e18 ≈ 962.0 rsETH
       Fair amount at 1.050:                              952.4 rsETH
       Excess minted:                                     ≈ 9.6 rsETH

Block N+k (stETH recovers):
  LRTOracle.updateRSETHPrice() called by anyone
       rsETHPrice recovers to ~1.050
  Attacker's 9.6 excess rsETH × 1.050 ≈ 10.1 ETH profit
  Extracted from existing holders via dilution.
``` [1](#0-0) [7](#0-6) [8](#0-7)

### Citations

**File:** contracts/LRTOracle.sol (L87-89)
```text
    function updateRSETHPrice() public whenNotPaused {
        _updateRsETHPrice();
    }
```

**File:** contracts/LRTOracle.sol (L214-316)
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
        }

        // downside protection — pause if price drops too far
        if (newRsETHPrice < highestRsethPrice) {
            uint256 diff = highestRsethPrice - newRsETHPrice;
            // normalizing to 1e18
            bool isPriceDecreaseOffLimit =
                pricePercentageLimit > 0 && diff > pricePercentageLimit.mulWad(highestRsethPrice);

            // if price decrease is off limit, pause the protocol (unless it's already paused)
            if (isPriceDecreaseOffLimit) {
                if (!lrtDepositPool.paused()) lrtDepositPool.pause();
                if (!withdrawalManager.paused()) withdrawalManager.pause();
                _pause();
                return;
            }

            // if price has decreased compared to the previous price, emit an event to reflect that
            if (previousPrice > newRsETHPrice) {
                emit RsETHPriceDecrease(newRsETHPrice, previousPrice);
            }

            // emit an event to notify that the price is currently below the peak (all time high) price
            emit RsETHPriceBelowPeak(highestRsethPrice, newRsETHPrice);
        }

        // update highest price if new price exceeds it
        if (newRsETHPrice > highestRsethPrice) {
            highestRsethPrice = newRsETHPrice;
        }

        // mint protocol fee as rsETH if there's a fee to take
        if (protocolFeeInETH > 0) {
            // Calculate rsETH amount to mint as protocol fee
            uint256 rsethAmountToMintAsProtocolFee = protocolFeeInETH.divWad(newRsETHPrice);

            _checkAndUpdateDailyFeeMintLimit(rsethAmountToMintAsProtocolFee);
            if (rsethAmountToMintAsProtocolFee > 0) {
                address treasury = lrtConfig.getContract(LRTConstants.PROTOCOL_TREASURY);
                IRSETH(rsETHTokenAddress).mint(treasury, rsethAmountToMintAsProtocolFee);
                emit FeeMinted(treasury, rsethAmountToMintAsProtocolFee);
            }
        } else {
            _checkAndUpdateDailyFeeMintLimit(0);
        }

        rsETHPrice = newRsETHPrice;

        emit RsETHPriceUpdate(rsETHPrice, previousPrice);
    }
```

**File:** contracts/LRTOracle.sol (L336-343)
```text
        for (uint16 assetIdx; assetIdx < supportedAssetCount;) {
            address asset = supportedAssets[assetIdx];
            // assetER is in 1e18 precision (1.0 = 1e18)
            uint256 assetER = getAssetPrice(asset);
            // totalAssetAmt is in 1e18 precision (standard token decimals)
            uint256 totalAssetAmt = ILRTDepositPool(lrtDepositPoolAddr).getTotalAssetDeposits(asset);

            totalETHInProtocol += totalAssetAmt.mulWad(assetER);
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
