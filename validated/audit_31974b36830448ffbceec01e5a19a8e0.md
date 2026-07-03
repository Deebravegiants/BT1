### Title
Single Failing Asset Price Oracle Blocks All rsETH Price Updates and Protocol Fee Minting - (File: contracts/LRTOracle.sol)

---

### Summary

`LRTOracle._getTotalEthInProtocol()` iterates through every supported asset and calls an external price oracle for each one inside the loop. There is no `try/catch` around these calls. If any single asset's price oracle reverts — due to being paused, returning a stale/invalid price, or a bug — the entire `updateRSETHPrice()` transaction reverts. This permanently freezes protocol fee (yield) accrual and leaves the stored `rsETHPrice` stale until an admin manually replaces the failing oracle.

---

### Finding Description

`_getTotalEthInProtocol()` is a private function called unconditionally by `_updateRsETHPrice()`, which is in turn called by the public `updateRSETHPrice()` and the manager-only `updateRSETHPriceAsManager()`.

```solidity
// contracts/LRTOracle.sol L331-L349
function _getTotalEthInProtocol() private view returns (uint256 totalETHInProtocol) {
    address lrtDepositPoolAddr = lrtConfig.getContract(LRTConstants.LRT_DEPOSIT_POOL);
    address[] memory supportedAssets = lrtConfig.getSupportedAssetList();
    uint256 supportedAssetCount = supportedAssets.length;

    for (uint16 assetIdx; assetIdx < supportedAssetCount;) {
        address asset = supportedAssets[assetIdx];
        uint256 assetER = getAssetPrice(asset);   // @audit external call, no try/catch
        uint256 totalAssetAmt = ILRTDepositPool(lrtDepositPoolAddr).getTotalAssetDeposits(asset);
        totalETHInProtocol += totalAssetAmt.mulWad(assetER);
        unchecked { ++assetIdx; }
    }
}
```

`getAssetPrice` delegates to an arbitrary `IPriceFetcher` contract:

```solidity
// contracts/LRTOracle.sol L156-L158
function getAssetPrice(address asset) public view onlySupportedOracle(asset) returns (uint256) {
    return IPriceFetcher(assetPriceOracle[asset]).getAssetPrice(asset);
}
```

If the `IPriceFetcher` for **any one** of the supported assets reverts (e.g., Chainlink circuit-breaker, oracle paused, sequencer down, stale-price guard), the revert propagates through `_getTotalEthInProtocol()` → `_updateRsETHPrice()` → `updateRSETHPrice()`, causing the entire call to fail. Both the public entry point and the manager-only entry point share the same code path and are equally affected. [1](#0-0) [2](#0-1) [3](#0-2) 

---

### Impact Explanation

`updateRSETHPrice()` is the sole mechanism that:
1. Computes the new `rsETHPrice` stored on-chain.
2. Calculates and mints the protocol fee in rsETH to the treasury.

When the function is blocked:

- **Protocol fee minting halts entirely.** Every call to `_updateRsETHPrice()` reverts before reaching the fee-minting logic at lines 299–311. Yield that has accrued in the protocol since the last successful update cannot be captured as fees. This constitutes **permanent freezing of unclaimed yield** for as long as the oracle remains broken.
- **`rsETHPrice` becomes stale.** Deposits (`getRsETHAmountToMint`) and withdrawal unlocks (`_createUnlockParams`) both read the stored `rsETHPrice`. A stale price causes users to receive incorrect rsETH amounts on deposit and incorrect asset amounts on withdrawal.

The manager can remediate by calling `updatePriceOracleFor(asset, newOracle)` to replace the failing oracle, but until that manual intervention occurs the protocol is in a degraded state — exactly the same dependency on manual intervention described in the reference report. [4](#0-3) [5](#0-4) 

---

### Likelihood Explanation

The protocol supports multiple LST assets, each backed by a separate `IPriceFetcher`. Real-world oracle failures are well-documented: Chainlink feeds have circuit-breakers that revert on deviation, sequencer-uptime feeds revert when the L2 sequencer is down, and custom price fetchers may have their own pause mechanisms. With N supported assets, the probability that at least one oracle reverts at any given time grows with N. No special attacker action is required — the failure can be triggered by normal market volatility or infrastructure events affecting any single integrated oracle. [6](#0-5) 

---

### Recommendation

Wrap the `getAssetPrice(asset)` call inside `_getTotalEthInProtocol()` in a `try/catch` block. On failure, either skip the asset (using its last known price as a fallback) or revert with a descriptive error that identifies the failing asset, allowing the manager to act on a specific oracle rather than having the entire price update silently fail or revert opaquely.

```solidity
try IPriceFetcher(assetPriceOracle[asset]).getAssetPrice(asset) returns (uint256 price) {
    uint256 totalAssetAmt = ILRTDepositPool(lrtDepositPoolAddr).getTotalAssetDeposits(asset);
    totalETHInProtocol += totalAssetAmt.mulWad(price);
} catch {
    revert AssetOracleFailed(asset); // or use last cached price
}
```

Alternatively, cache the last valid price per asset and fall back to it when the live call reverts, so a single oracle outage does not halt the entire price update.

---

### Proof of Concept

1. Protocol has N supported assets (e.g., ETH, stETH, cbETH).
2. The Chainlink feed for `cbETH` activates its circuit-breaker and begins reverting.
3. Any caller (including a keeper bot or the manager) calls `updateRSETHPrice()`.
4. `_updateRsETHPrice()` calls `_getTotalEthInProtocol()`.
5. The loop reaches `cbETH`, calls `getAssetPrice(cbETH)`, which calls `IPriceFetcher(assetPriceOracle[cbETH]).getAssetPrice(cbETH)` — this reverts.
6. The revert bubbles up through `_getTotalEthInProtocol()` → `_updateRsETHPrice()` → `updateRSETHPrice()`.
7. `rsETHPrice` is not updated; protocol fee is not minted.
8. All subsequent calls to `updateRSETHPrice()` and `updateRSETHPriceAsManager()` revert identically.
9. Unclaimed yield accumulates but cannot be captured until the admin calls `updatePriceOracleFor(cbETH, newOracle)`. [7](#0-6) [8](#0-7)

### Citations

**File:** contracts/LRTOracle.sol (L26-26)
```text
    mapping(address asset => address priceOracle) public override assetPriceOracle;
```

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

**File:** contracts/LRTOracle.sol (L113-118)
```text
    function updatePriceOracleFor(address asset, address priceOracle) public onlyLRTAdmin {
        if (lrtConfig.isSupportedAsset(asset)) {
            UtilLib.checkNonZeroAddress(priceOracle);
        }
        assetPriceOracle[asset] = priceOracle;
        emit AssetPriceOracleUpdate(asset, priceOracle);
```

**File:** contracts/LRTOracle.sol (L156-158)
```text
    function getAssetPrice(address asset) public view onlySupportedOracle(asset) returns (uint256) {
        return IPriceFetcher(assetPriceOracle[asset]).getAssetPrice(asset);
    }
```

**File:** contracts/LRTOracle.sol (L231-231)
```text
        uint256 totalETHInProtocol = _getTotalEthInProtocol();
```

**File:** contracts/LRTOracle.sol (L299-313)
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

        rsETHPrice = newRsETHPrice;
```

**File:** contracts/LRTOracle.sol (L336-349)
```text
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
