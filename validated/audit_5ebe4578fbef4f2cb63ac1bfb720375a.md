### Title
Stale `rsETHPrice` Used in Deposit Calculation Before Fee Minting Update — (File: `contracts/LRTDepositPool.sol`)

---

### Summary

`LRTDepositPool.getRsETHAmountToMint()` uses the stored `lrtOracle.rsETHPrice()` without first triggering `updateRSETHPrice()`. Because `updateRSETHPrice()` is the function that mints protocol fee rsETH and refreshes the stored price to reflect accumulated staking rewards, any deposit made while the price is stale (i.e., TVL has grown since the last update) causes the depositor to receive more rsETH than they deserve, stealing unclaimed yield from existing holders.

---

### Finding Description

`LRTOracle` stores `rsETHPrice` as a plain state variable: [1](#0-0) 

It is only refreshed when `updateRSETHPrice()` / `_updateRsETHPrice()` is explicitly called. Inside `_updateRsETHPrice()`, the sequence is:

1. Read current `rsethSupply` (pre-fee-mint totalSupply): [2](#0-1) 
2. Compute `newRsETHPrice` using that pre-fee supply: [3](#0-2) 
3. Mint protocol fee rsETH to treasury (increases totalSupply): [4](#0-3) 
4. Persist `rsETHPrice = newRsETHPrice`: [5](#0-4) 

Between two consecutive calls to `updateRSETHPrice()`, staking rewards accumulate and TVL grows while `totalSupply` stays constant. This makes the stored `rsETHPrice` **lower** than the true current price.

When a user calls `depositETH()` or `depositAsset()`, the deposit flow reaches `getRsETHAmountToMint()`:

```solidity
rsethAmountToMint = (amount * lrtOracle.getAssetPrice(asset)) / lrtOracle.rsETHPrice();
``` [6](#0-5) 

`lrtOracle.rsETHPrice()` returns the **stale stored value** — no call to `updateRSETHPrice()` is made anywhere in the deposit path. Because the denominator (`rsETHPrice`) is lower than the true price, the depositor receives **more rsETH than they deserve**. The longer the interval since the last `updateRSETHPrice()` call, the larger the excess — exactly mirroring the original report's statement: *"The longer the period since the last `mintFee` was called the more excess tokens the user receives."*

The same stale price is used in `getExpectedAssetAmount()` for withdrawals:

```solidity
underlyingToReceive = amount * lrtOracle.rsETHPrice() / lrtOracle.getAssetPrice(asset);
``` [7](#0-6) 

---

### Impact Explanation

Depositors calling `depositETH()` or `depositAsset()` while `rsETHPrice` is stale receive excess rsETH. This excess represents a share of the staking rewards that have accrued since the last price update — rewards that rightfully belong to existing rsETH holders. Existing holders' rsETH is diluted beyond what the protocol fee mechanism intends, constituting **theft of unclaimed yield** (High impact).

---

### Likelihood Explanation

Staking rewards accumulate every block. `updateRSETHPrice()` is a standalone public function that must be called explicitly — it is not invoked automatically within the deposit or withdrawal flow. Any deposit made in the interval between two `updateRSETHPrice()` calls (which in practice can span hours or days) exploits the stale price. No special permissions or conditions are required; any unprivileged depositor can trigger this path.

---

### Recommendation

Call `updateRSETHPrice()` (or an equivalent internal price-refresh) at the beginning of `_beforeDeposit()` in `LRTDepositPool`, before `getRsETHAmountToMint()` reads `rsETHPrice`. This mirrors the original report's recommendation to call `mintFee` before computing the share ratio.

---

### Proof of Concept

1. Protocol state: TVL = 1 000 ETH, rsETH `totalSupply` = 1 000, stored `rsETHPrice` = 1.0 ETH. `updateRSETHPrice()` was last called at this point.
2. Staking rewards accumulate: TVL grows to 1 010 ETH. `updateRSETHPrice()` has **not** been called. Stored `rsETHPrice` remains 1.0 ETH (stale).
3. True price (after protocol fee, e.g. 10 % of 10 ETH reward = 1 ETH fee): `(1010 − 1) / 1000 ≈ 1.009 ETH`.
4. Attacker calls `depositETH{value: 10 ether}(0, "")`.
   - `getRsETHAmountToMint` computes: `10 * 1e18 / 1.0e18 = 10 rsETH`.
   - Correct amount at true price: `10 / 1.009 ≈ 9.91 rsETH`.
   - Excess received: **≈ 0.09 rsETH** stolen from existing holders.
5. When `updateRSETHPrice()` is eventually called, it mints fee rsETH to treasury and updates the price — but the attacker's excess rsETH is already minted and irrecoverable. [8](#0-7) [9](#0-8) [10](#0-9)

### Citations

**File:** contracts/LRTOracle.sol (L28-28)
```text
    uint256 public override rsETHPrice;
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

**File:** contracts/LRTDepositPool.sol (L76-92)
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

**File:** contracts/LRTWithdrawalManager.sol (L593-593)
```text
        underlyingToReceive = amount * lrtOracle.rsETHPrice() / lrtOracle.getAssetPrice(asset);
```
