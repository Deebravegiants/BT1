### Title
Single Reverting Price Oracle Permanently DOS's `updateRSETHPrice()`, Freezing Protocol Fee Yield — (`contracts/LRTOracle.sol`)

---

### Summary

`LRTOracle._getTotalEthInProtocol()` iterates over every supported asset and makes an unguarded external call to each asset's price oracle. If any single oracle reverts, the entire `updateRSETHPrice()` call reverts. Because `updateRSETHPrice()` is the sole mechanism for minting protocol fee yield (rsETH) to the treasury, a single malfunctioning oracle permanently freezes all accrued protocol yield and disables the downside-protection auto-pause.

---

### Finding Description

`_getTotalEthInProtocol()` is called inside `_updateRsETHPrice()`, which is the body of the public `updateRSETHPrice()` function:

```solidity
// LRTOracle.sol lines 331-349
function _getTotalEthInProtocol() private view returns (uint256 totalETHInProtocol) {
    address lrtDepositPoolAddr = lrtConfig.getContract(LRTConstants.LRT_DEPOSIT_POOL);
    address[] memory supportedAssets = lrtConfig.getSupportedAssetList();
    uint256 supportedAssetCount = supportedAssets.length;

    for (uint16 assetIdx; assetIdx < supportedAssetCount;) {
        address asset = supportedAssets[assetIdx];
        uint256 assetER = getAssetPrice(asset);          // ← external call, no try/catch
        uint256 totalAssetAmt = ILRTDepositPool(lrtDepositPoolAddr).getTotalAssetDeposits(asset);
        totalETHInProtocol += totalAssetAmt.mulWad(assetER);
        unchecked { ++assetIdx; }
    }
}
``` [1](#0-0) 

`getAssetPrice(asset)` delegates to an external `IPriceFetcher` contract:

```solidity
// LRTOracle.sol line 157
return IPriceFetcher(assetPriceOracle[asset]).getAssetPrice(asset);
``` [2](#0-1) 

There is no `try/catch` around this call. If the oracle for **any one** supported asset reverts (e.g., Chainlink reverts on a stale answer, a sequencer-down check, or a deprecated aggregator), the entire `_getTotalEthInProtocol()` reverts, which causes `_updateRsETHPrice()` to revert, which causes `updateRSETHPrice()` to revert.

A second nested exposure exists inside `getTotalAssetDeposits()` → `getAssetDistributionData()`, which is also called from within `_getTotalEthInProtocol()`. That function loops over every NodeDelegator and makes unguarded external calls to `getAssetBalance()` and `getAssetUnstaking()` on each:

```solidity
// LRTDepositPool.sol lines 447-456
for (uint256 i; i < ndcsCount;) {
    assetLyingInNDCs += IERC20(asset).balanceOf(nodeDelegatorQueue[i]);
    assetStakedInEigenLayer += INodeDelegator(nodeDelegatorQueue[i]).getAssetBalance(asset);
    assetUnstakingFromEigenLayer += INodeDelegator(nodeDelegatorQueue[i]).getAssetUnstaking(asset);
    unchecked { ++i; }
}
``` [3](#0-2) 

`getAssetUnstaking()` itself makes an external call to EigenLayer's `DelegationManager.getQueuedWithdrawals()`:

```solidity
// NodeDelegator.sol lines 406-407
(IDelegationManager.Withdrawal[] memory queuedWithdrawals, uint256[][] memory withdrawalShares) =
    _getDelegationManager().getQueuedWithdrawals(address(this));
``` [4](#0-3) 

Any revert in this chain propagates all the way up to `updateRSETHPrice()`.

---

### Impact Explanation

`_updateRsETHPrice()` is the only place where protocol fee rsETH is minted to the treasury:

```solidity
// LRTOracle.sol lines 304-307
if (rsethAmountToMintAsProtocolFee > 0) {
    address treasury = lrtConfig.getContract(LRTConstants.PROTOCOL_TREASURY);
    IRSETH(rsETHTokenAddress).mint(treasury, rsethAmountToMintAsProtocolFee);
``` [5](#0-4) 

If `updateRSETHPrice()` is permanently DOS'd:

1. **Permanent freezing of unclaimed yield** — all protocol fee rsETH that would have been minted to the treasury is permanently lost. This matches the "Medium — Permanent freezing of unclaimed yield" impact tier.
2. **Downside-protection auto-pause disabled** — the price-drop circuit breaker that pauses `LRTDepositPool` and `LRTWithdrawalManager` can never fire, leaving the protocol exposed to undetected slashing events.

```solidity
// LRTOracle.sol lines 277-281
if (isPriceDecreaseOffLimit) {
    if (!lrtDepositPool.paused()) lrtDepositPool.pause();
    if (!withdrawalManager.paused()) withdrawalManager.pause();
    _pause();
    return;
}
``` [6](#0-5) 

---

### Likelihood Explanation

`updateRSETHPrice()` is a public function callable by anyone:

```solidity
// LRTOracle.sol line 87
function updateRSETHPrice() public whenNotPaused {
``` [7](#0-6) 

The protocol supports multiple LST assets (stETH, ETHx, sfrxETH, swETH, rETH), each with its own price oracle. Chainlink oracles are known to revert when: the sequencer is down (L2), the answer is stale beyond the heartbeat, or the aggregator is deprecated and replaced. Any one of these conditions on any one supported asset's oracle is sufficient to trigger the DOS. The likelihood is **Medium** — it is a realistic, non-adversarial scenario that has occurred on mainnet for other protocols.

---

### Recommendation

Wrap each oracle call in a `try/catch` block inside `_getTotalEthInProtocol()`. If an oracle reverts, either skip that asset (with an event) or revert with a descriptive error that identifies the failing oracle, allowing the admin to replace it without blocking the entire price update. Similarly, wrap the NDC loop calls in `getAssetDistributionData()` with error handling so a single broken NodeDelegator cannot block the entire accounting path.

---

### Proof of Concept

1. Protocol has three supported assets: stETH, ETHx, sfrxETH.
2. The Chainlink aggregator for sfrxETH is deprecated and begins reverting on `latestRoundData()`.
3. Any call to `updateRSETHPrice()` now reverts at `getAssetPrice(sfrxETH)` inside `_getTotalEthInProtocol()`.
4. Protocol fee rsETH can no longer be minted to the treasury — all yield accrued from that point forward is permanently frozen.
5. The price-drop auto-pause circuit breaker is also disabled; if stETH is slashed, the protocol cannot auto-pause to protect depositors.
6. The only remediation path is an admin upgrade to replace the oracle, but until that upgrade is executed and the timelock delay passes, the DOS persists. [8](#0-7) [1](#0-0)

### Citations

**File:** contracts/LRTOracle.sol (L87-89)
```text
    function updateRSETHPrice() public whenNotPaused {
        _updateRsETHPrice();
    }
```

**File:** contracts/LRTOracle.sol (L156-158)
```text
    function getAssetPrice(address asset) public view onlySupportedOracle(asset) returns (uint256) {
        return IPriceFetcher(assetPriceOracle[asset]).getAssetPrice(asset);
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

**File:** contracts/LRTDepositPool.sol (L447-456)
```text
        for (uint256 i; i < ndcsCount;) {
            assetLyingInNDCs += IERC20(asset).balanceOf(nodeDelegatorQueue[i]);

            assetStakedInEigenLayer += INodeDelegator(nodeDelegatorQueue[i]).getAssetBalance(asset);
            assetUnstakingFromEigenLayer += INodeDelegator(nodeDelegatorQueue[i]).getAssetUnstaking(asset);

            unchecked {
                ++i;
            }
        }
```

**File:** contracts/NodeDelegator.sol (L406-407)
```text
        (IDelegationManager.Withdrawal[] memory queuedWithdrawals, uint256[][] memory withdrawalShares) =
            _getDelegationManager().getQueuedWithdrawals(address(this));
```
