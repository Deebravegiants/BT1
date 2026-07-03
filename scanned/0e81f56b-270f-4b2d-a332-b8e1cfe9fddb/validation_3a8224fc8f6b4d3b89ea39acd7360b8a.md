### Title
Stale `rsETHPrice` Allows Reward Sniping Before Oracle Update, Diluting Existing Holders' Yield - (File: `contracts/LRTOracle.sol`)

---

### Summary

`LRTOracle` stores `rsETHPrice` as a state variable that is only updated on explicit calls to `updateRSETHPrice()`. Between reward accrual events (e.g., MEV rewards forwarded by `FeeReceiver.sendFunds()`) and the next price update, the stored price is stale. Any depositor who calls `depositETH()` or `depositAsset()` during this window receives more rsETH than they deserve, capturing a portion of the accumulated yield that belongs to existing holders.

---

### Finding Description

`LRTOracle._updateRsETHPrice()` computes the new rsETH price as:

```
newRsETHPrice = (totalETHInProtocol - protocolFeeInETH) / rsethSupply
```

and writes it to the storage variable `rsETHPrice`. [1](#0-0) 

This update is **not automatic**. It only happens when `updateRSETHPrice()` (public, callable by anyone) or `updateRSETHPriceAsManager()` is explicitly invoked. [2](#0-1) 

Meanwhile, `FeeReceiver.sendFunds()` is also public and permissionless — it forwards the entire ETH balance of `FeeReceiver` (MEV/execution-layer rewards) directly into `LRTDepositPool` via `receiveFromRewardReceiver()`, immediately increasing the protocol's TVL without touching `rsETHPrice`. [3](#0-2) 

`LRTDepositPool.getETHDistributionData()` includes `address(this).balance` in the TVL, so the newly received ETH is immediately counted in `_getTotalEthInProtocol()`. [4](#0-3) 

`LRTDepositPool.getRsETHAmountToMint()` uses the **stored** (stale) `rsETHPrice`:

```solidity
rsethAmountToMint = (amount * lrtOracle.getAssetPrice(asset)) / lrtOracle.rsETHPrice();
``` [5](#0-4) 

Because `rsETHPrice` is lower than the true current value, the depositor receives more rsETH than their deposit warrants.

**Concrete numeric example:**

| State | Value |
|---|---|
| rsETH supply | 100 |
| Stored `rsETHPrice` | 1.0 ETH (stale) |
| Actual TVL after rewards | 110 ETH |
| True price | 1.1 ETH |

Attacker deposits 10 ETH at stale price → receives `10 / 1.0 = 10 rsETH` (should receive `10 / 1.1 ≈ 9.09 rsETH`).

After `updateRSETHPrice()`:
- Supply = 110, TVL = 120 ETH
- `previousTVL = 110 × 1.0 = 110`, `rewardAmount = 10 ETH`
- `newRsETHPrice = (120 − fee) / 110 ≈ 1.09 ETH`

Attacker holds 10 rsETH × 1.09 = **10.9 ETH** (deposited 10 ETH → gained ~0.9 ETH).  
Original 100-rsETH holders now hold 100 × 1.09 = **109 ETH** instead of the expected **110 ETH** — they lost ~1 ETH of yield.

---

### Impact Explanation

Existing rsETH holders lose a portion of their accumulated staking/MEV yield to any depositor who deposits between a reward accrual event and the next `updateRSETHPrice()` call. This is **theft of unclaimed yield** (High severity per the allowed impact scope).

---

### Likelihood Explanation

Both `FeeReceiver.sendFunds()` and `updateRSETHPrice()` are public and permissionless. An attacker can:
1. Monitor the mempool for `FeeReceiver.sendFunds()` or watch `FeeReceiver.balance` on-chain.
2. Call `FeeReceiver.sendFunds()` themselves to push rewards into the deposit pool.
3. Immediately call `depositETH()` at the stale price in the same block (or front-run the price update).
4. Call `updateRSETHPrice()` to crystallize the gain.

This requires no privileged access and is repeatable every reward cycle. Likelihood is **High**.

---

### Recommendation

Atomically update `rsETHPrice` before computing the rsETH mint amount in `getRsETHAmountToMint()`, or call `_updateRsETHPrice()` at the start of `_beforeDeposit()`. This ensures deposits always use the current price inclusive of any accrued rewards:

```solidity
function _beforeDeposit(...) private returns (uint256 rsethAmountToMint) {
    // Sync price before computing mint amount
    ILRTOracle(lrtConfig.getContract(LRTConstants.LRT_ORACLE)).updateRSETHPrice();
    ...
    rsethAmountToMint = getRsETHAmountToMint(asset, depositAmount);
    ...
}
```

Alternatively, `getRsETHAmountToMint()` can compute the live price on-the-fly from `_getTotalEthInProtocol() / rsethSupply` rather than reading the stored `rsETHPrice`.

---

### Proof of Concept

1. Deploy the protocol with 100 rsETH outstanding at price 1.0 ETH (TVL = 100 ETH).
2. Call `FeeReceiver.sendFunds()` to push 10 ETH of MEV rewards into `LRTDepositPool` (TVL becomes 110 ETH; `rsETHPrice` remains 1.0).
3. Attacker calls `depositETH{value: 10 ether}(0, "")` — receives 10 rsETH (correct would be ≈9.09).
4. Call `updateRSETHPrice()` — new price ≈ 1.09 ETH.
5. Attacker's 10 rsETH is now worth ≈10.9 ETH; original holders' 100 rsETH is worth ≈109 ETH instead of 110 ETH.
6. Attacker redeems, extracting ~0.9 ETH of yield that belonged to existing holders.

Relevant code path: [3](#0-2) [6](#0-5) [7](#0-6) [8](#0-7) [9](#0-8)

### Citations

**File:** contracts/LRTOracle.sol (L87-96)
```text
    function updateRSETHPrice() public whenNotPaused {
        _updateRsETHPrice();
    }

    /// @dev update rsETH price as an manager account
    /// @dev main benefit is to be able to update the price in case of the price going above the threshold
    /// @dev only LRT manager is allowed to call this function
    function updateRSETHPriceAsManager() external onlyLRTManager {
        _updateRsETHPrice();
    }
```

**File:** contracts/LRTOracle.sol (L214-313)
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
```

**File:** contracts/FeeReceiver.sol (L53-57)
```text
    function sendFunds() external {
        uint256 balance = address(this).balance;
        ILRTDepositPool(depositPool).receiveFromRewardReceiver{ value: balance }();

        emit MevRewardsAddedToTVL(balance);
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
