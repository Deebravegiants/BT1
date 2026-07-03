### Title
DoS of `updateRSETHPrice()` via Single Failing External Oracle in `_getTotalEthInProtocol()` Loop — (`contracts/LRTOracle.sol`)

---

### Summary

`LRTOracle._getTotalEthInProtocol()` iterates over every supported asset and makes two external calls per iteration — one to an external price oracle and one to `LRTDepositPool.getTotalAssetDeposits()` (which itself fans out to EigenLayer via NodeDelegators). If any single external call reverts, the entire `updateRSETHPrice()` transaction reverts. Because `rsETHPrice` is a stored value that can only be updated through this function, a sustained failure permanently freezes the price used for all deposits and withdrawals, disables the protocol's auto-pause downside-protection mechanism, and permanently freezes unclaimed protocol fee yield.

---

### Finding Description

`_getTotalEthInProtocol()` is the private function called by both the public `updateRSETHPrice()` and the manager-only `updateRSETHPriceAsManager()`:

```solidity
// contracts/LRTOracle.sol:331-349
function _getTotalEthInProtocol() private view returns (uint256 totalETHInProtocol) {
    address lrtDepositPoolAddr = lrtConfig.getContract(LRTConstants.LRT_DEPOSIT_POOL);
    address[] memory supportedAssets = lrtConfig.getSupportedAssetList();
    uint256 supportedAssetCount = supportedAssets.length;

    for (uint16 assetIdx; assetIdx < supportedAssetCount;) {
        address asset = supportedAssets[assetIdx];
        uint256 assetER = getAssetPrice(asset);                                          // ← external oracle call
        uint256 totalAssetAmt = ILRTDepositPool(lrtDepositPoolAddr).getTotalAssetDeposits(asset); // ← fans out to EigenLayer

        totalETHInProtocol += totalAssetAmt.mulWad(assetER);
        unchecked { ++assetIdx; }
    }
}
``` [1](#0-0) 

`getAssetPrice(asset)` delegates unconditionally to an external `IPriceFetcher`:

```solidity
// contracts/LRTOracle.sol:156-158
function getAssetPrice(address asset) public view onlySupportedOracle(asset) returns (uint256) {
    return IPriceFetcher(assetPriceOracle[asset]).getAssetPrice(asset);
}
``` [2](#0-1) 

Concrete revert scenarios for each oracle type already in scope:

- **`EthXPriceOracle`** — calls `IETHXStakePoolsManager.getExchangeRate()` on Stader's external contract; if Stader pauses or upgrades, this reverts. [3](#0-2) 
- **`RETHPriceOracle`** — calls `IrETH.getExchangeRate()` on Rocket Pool's rETH token; if Rocket Pool's storage is migrated or the contract is paused, this reverts. [4](#0-3) 
- **`SwETHPriceOracle`** — calls `ISwETH.getRate()` on Swell's external contract; same failure mode. [5](#0-4) 

`getTotalAssetDeposits()` also fans out to every NodeDelegator and calls EigenLayer's `getWithdrawableShares` and `getQueuedWithdrawals`, adding further external revert surface. [6](#0-5) 

Because there is no `try/catch` anywhere in this loop, a single revert in any of these external calls causes `_updateRsETHPrice()` to revert entirely, leaving `rsETHPrice` frozen at its last stored value. [7](#0-6) 

---

### Impact Explanation

Three compounding impacts result from a frozen `rsETHPrice`:

1. **Permanent freezing of unclaimed yield (High).** `_updateRsETHPrice()` is the only place protocol fees are minted to the treasury. If it is blocked, no fees are ever minted regardless of how much ETH accrues. [8](#0-7) 

2. **Temporary freezing of funds (Medium).** The stored `rsETHPrice` is consumed directly by `LRTWithdrawalManager._createUnlockParams()` to compute withdrawal payouts. A stale price means withdrawal unlock amounts are computed incorrectly for the entire duration of the freeze. [9](#0-8) 

3. **Auto-pause downside protection disabled (Medium→Critical escalation path).** `_updateRsETHPrice()` contains the only logic that auto-pauses `LRTDepositPool` and `LRTWithdrawalManager` when the price drops beyond `pricePercentageLimit`. If the function is DoS'd, a real slashing event will not trigger the circuit breaker, leaving the protocol open to continued deposits and withdrawals at a price that no longer reflects actual collateral. [10](#0-9) 

---

### Likelihood Explanation

Each supported LST oracle wraps an external protocol contract. Any of the following realistic events causes a revert:

- Stader, Rocket Pool, or Swell pauses their rate-reporting contract during an upgrade or incident.
- EigenLayer's `DelegationManager` or `StrategyManager` is paused (EigenLayer has a multi-sig pause mechanism).
- A NodeDelegator's EigenPod enters an inconsistent state causing `getQueuedWithdrawals` to revert.

The protocol currently supports multiple LSTs, so the attack surface grows with each new asset added. No attacker action is required — normal external protocol maintenance is sufficient to trigger the condition.

---

### Recommendation

Wrap each per-asset external call in a `try/catch` block inside `_getTotalEthInProtocol()`. If an oracle call fails, either skip that asset (with an emitted warning event) or revert with a descriptive error that identifies the failing asset, allowing the admin to temporarily remove the broken oracle via `updatePriceOracleFor()` without blocking the entire price update. Example pattern:

```solidity
try IPriceFetcher(assetPriceOracle[asset]).getAssetPrice(asset) returns (uint256 price) {
    assetER = price;
} catch {
    emit AssetOracleFailed(asset);
    continue; // or revert with asset-specific error
}
```

Additionally, consider separating the fee-minting logic from the price-update loop so that a single oracle failure does not also block fee accrual.

---

### Proof of Concept

1. Protocol has three supported assets: stETH, ETHx, rETH.
2. Stader pauses `IETHXStakePoolsManager` for a contract upgrade — `getExchangeRate()` reverts.
3. Any caller (including a keeper bot or any user) calls `updateRSETHPrice()`.
4. `_getTotalEthInProtocol()` reaches the ETHx iteration, calls `getAssetPrice(ethx)`, which calls `IETHXStakePoolsManager.getExchangeRate()` — reverts.
5. The entire transaction reverts. `rsETHPrice` is not updated.
6. For the duration of the Stader upgrade (hours to days), `rsETHPrice` is frozen.
7. Protocol fees are not minted for that period — permanent loss of yield for the treasury.
8. If a slashing event occurs during this window, the auto-pause circuit breaker at `LRTOracle.sol:277-281` never fires, leaving the protocol unprotected. [11](#0-10) [3](#0-2)

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

**File:** contracts/LRTOracle.sol (L270-281)
```text
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
```

**File:** contracts/LRTOracle.sol (L299-311)
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
        } else {
            _checkAndUpdateDailyFeeMintLimit(0);
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

**File:** contracts/oracles/EthXPriceOracle.sol (L46-52)
```text
    function getAssetPrice(address asset) external view returns (uint256) {
        if (asset != ethxAddress) {
            revert InvalidAsset();
        }

        return IETHXStakePoolsManager(ethXStakePoolsManagerProxyAddress).getExchangeRate();
    }
```

**File:** contracts/oracles/RETHPriceOracle.sol (L34-40)
```text
    function getAssetPrice(address asset) external view returns (uint256) {
        if (asset != rETHAddress) {
            revert InvalidAsset();
        }

        return IrETH(rETHAddress).getExchangeRate();
    }
```

**File:** contracts/oracles/SwETHPriceOracle.sol (L34-40)
```text
    function getAssetPrice(address asset) external view returns (uint256) {
        if (asset != swETHAddress) {
            revert InvalidAsset();
        }

        return ISwETH(swETHAddress).getRate();
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

**File:** contracts/LRTWithdrawalManager.sol (L846-850)
```text
        return UnlockParams({
            rsETHPrice: lrtOracle.rsETHPrice(),
            assetPrice: lrtOracle.getAssetPrice(asset),
            totalAvailableAssets: unstakingVault.balanceOf(asset)
        });
```
