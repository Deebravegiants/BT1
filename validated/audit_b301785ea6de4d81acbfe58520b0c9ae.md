### Title
Unrestricted `updateRSETHPrice()` Allows Any Caller to Trigger Protocol Fee Minting, Diluting rsETH Holders - (File: contracts/LRTOracle.sol)

---

### Summary

`LRTOracle.updateRSETHPrice()` carries no role-based access control — only a `whenNotPaused` guard — allowing any unprivileged external account to invoke the internal `_updateRsETHPrice()` logic, which mints rsETH as protocol fees to the treasury whenever TVL has grown since the last update. This is the direct analog of the reported Monoswap `updatePoolPrice` missing-access-control pattern.

---

### Finding Description

`updateRSETHPrice()` is declared `public whenNotPaused` with no role check:

```solidity
// contracts/LRTOracle.sol line 87
function updateRSETHPrice() public whenNotPaused {
    _updateRsETHPrice();
}
```

The protocol itself acknowledges that privileged access is needed for price updates in certain conditions — a separate entry point `updateRSETHPriceAsManager()` exists with `onlyLRTManager`:

```solidity
// contracts/LRTOracle.sol line 94
function updateRSETHPriceAsManager() external onlyLRTManager {
    _updateRsETHPrice();
}
```

Both call the same `_updateRsETHPrice()` internal function, which computes and mints protocol fees:

```solidity
// contracts/LRTOracle.sol lines 244–246
if (!protocolPaused && totalETHInProtocol > previousTVL) {
    uint256 rewardAmount = totalETHInProtocol - previousTVL;
    protocolFeeInETH = (rewardAmount * lrtConfig.protocolFeeInBPS()) / 10_000;
}
```

```solidity
// contracts/LRTOracle.sol lines 304–307
address treasury = lrtConfig.getContract(LRTConstants.PROTOCOL_TREASURY);
IRSETH(rsETHTokenAddress).mint(treasury, rsethAmountToMintAsProtocolFee);
emit FeeMinted(treasury, rsethAmountToMintAsProtocolFee);
```

The daily fee cap (`maxFeeMintAmountPerDay`) enforced by `_checkAndUpdateDailyFeeMintLimit` is the only bound on how much can be minted per 24-hour window, but it does not restrict *who* can trigger the minting. [1](#0-0) [2](#0-1) [3](#0-2) [4](#0-3) [5](#0-4) 

---

### Impact Explanation

**High — Theft of unclaimed yield.**

When staking rewards accrue and TVL rises, the protocol is designed to take a fee (in rsETH) from that yield and send it to the treasury. This fee dilutes existing rsETH holders proportionally. Any unprivileged caller — a depositor, rsETH holder, or external contract — can call `updateRSETHPrice()` at any moment to trigger this fee minting. The attacker can:

1. Monitor TVL growth off-chain.
2. Call `updateRSETHPrice()` immediately after any TVL increase, before the protocol's own keeper does.
3. Repeat up to the daily cap each day.

The result is that yield that would otherwise remain accrued to rsETH holders (until a legitimate, authorized price update) is extracted as protocol fees on the attacker's schedule, maximizing dilution of holders' unclaimed yield. [6](#0-5) [7](#0-6) 

---

### Likelihood Explanation

**High.** The function is `public`, requires no ETH, no tokens, and no special role. Any EOA or contract can call it at any time the oracle is not paused. The attacker only needs to observe that TVL has increased (trivially detectable on-chain) and submit a transaction. [8](#0-7) 

---

### Recommendation

Restrict `updateRSETHPrice()` to a trusted keeper role (e.g., `onlyLRTManager` or a dedicated `KEEPER_ROLE`), consistent with the already-existing `updateRSETHPriceAsManager()` pattern. Alternatively, separate the price-read update from the fee-minting step so that fee minting requires explicit privileged authorization. [9](#0-8) 

---

### Proof of Concept

1. Staking rewards accrue in EigenLayer; `_getTotalEthInProtocol()` now returns a value greater than `rsethSupply * rsETHPrice` (i.e., `totalETHInProtocol > previousTVL`).
2. Attacker (any EOA) calls `LRTOracle.updateRSETHPrice()` directly — no role required.
3. Inside `_updateRsETHPrice()`:
   - `protocolFeeInETH = rewardAmount * protocolFeeInBPS / 10_000` is computed.
   - `rsethAmountToMintAsProtocolFee = protocolFeeInETH / newRsETHPrice` is computed.
   - `_checkAndUpdateDailyFeeMintLimit(rsethAmountToMintAsProtocolFee)` passes (within daily cap).
   - `IRSETH(rsETHTokenAddress).mint(treasury, rsethAmountToMintAsProtocolFee)` executes — new rsETH is minted to the treasury.
4. All existing rsETH holders are diluted by the newly minted supply, losing a portion of their unclaimed yield to the treasury, triggered by an unauthorized party. [10](#0-9)

### Citations

**File:** contracts/LRTOracle.sol (L85-89)
```text
    /// @notice updates RSETH/ETH exchange rate
    /// @dev calculates rsETH price based on stakedAsset value received from EigenLayer
    function updateRSETHPrice() public whenNotPaused {
        _updateRsETHPrice();
    }
```

**File:** contracts/LRTOracle.sol (L91-96)
```text
    /// @dev update rsETH price as an manager account
    /// @dev main benefit is to be able to update the price in case of the price going above the threshold
    /// @dev only LRT manager is allowed to call this function
    function updateRSETHPriceAsManager() external onlyLRTManager {
        _updateRsETHPrice();
    }
```

**File:** contracts/LRTOracle.sol (L197-210)
```text
    function _checkAndUpdateDailyFeeMintLimit(uint256 feeAmount) internal {
        // Reset the period if it's unset or a day has passed
        if (block.timestamp >= feePeriodStartTime + 1 days) {
            currentPeriodMintedFeeAmount = 0;
            feePeriodStartTime = getCurrentPeriodStartTime();
        }

        // Check if minting would exceed the daily limit
        if (currentPeriodMintedFeeAmount + feeAmount > maxFeeMintAmountPerDay) {
            revert DailyFeeMintLimitExceeded(currentPeriodMintedFeeAmount + feeAmount, maxFeeMintAmountPerDay);
        }

        currentPeriodMintedFeeAmount += feeAmount;
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
