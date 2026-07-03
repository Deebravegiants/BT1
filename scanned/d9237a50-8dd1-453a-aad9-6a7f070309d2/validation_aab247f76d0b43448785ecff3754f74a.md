### Title
Stale `ethValueInWithdrawal` After Lido Negative Rebase Creates Permanent Phantom TVL — (`contracts/LRTConverter.sol`)

---

### Summary

When stETH is transferred from the deposit pool to `LRTConverter`, its ETH value is snapshotted into `ethValueInWithdrawal` at the current oracle price. Because stETH is a rebasing token, a Lido slashing event reduces the actual stETH balance held by the converter without updating `ethValueInWithdrawal`. After the full unstake-and-claim cycle, the ETH actually received from Lido (post-slash, less than the snapshot) is subtracted from `ethValueInWithdrawal`, leaving a permanent residual phantom ETH value that inflates `rsETHPrice` indefinitely.

---

### Finding Description

**Step 1 — Snapshot at transfer time.**

`LRTConverter.transferAssetFromDepositPool` records the ETH value of the transferred stETH using the oracle price at the moment of transfer:

```solidity
ethValueInWithdrawal += (_amount * lrtOracle.getAssetPrice(_asset)) / 1e18;
``` [1](#0-0) 

This value is never automatically updated when the underlying stETH balance changes due to a rebase.

**Step 2 — Converter accounting uses the stale snapshot.**

`LRTDepositPool.getETHDistributionData` reads `ethValueInWithdrawal` directly as the ETH value of all assets in the converter:

```solidity
ethLyingInConverter = ILRTConverter(lrtConverter).ethValueInWithdrawal();
``` [2](#0-1) 

Simultaneously, `getAssetDistributionData(stETH)` explicitly zeroes out the converter contribution for stETH:

```solidity
assetLyingInConverter = 0; // assets in converter are accounted in their eth value => getETHDistributionData()
``` [3](#0-2) 

So the stETH in the converter is counted **only** through `ethValueInWithdrawal`, never through a live `balanceOf` call.

**Step 3 — Negative rebase creates divergence.**

After a Lido slash, stETH's `balanceOf` for the converter decreases (e.g., 100 stETH → 95 stETH), but `ethValueInWithdrawal` remains at the pre-slash value (100 ETH). The TVL reported by `_getTotalEthInProtocol` is overstated by 5 ETH. [4](#0-3) 

**Step 4 — Phantom residual after claim.**

When the operator eventually calls `unstakeStEth` and `claimStEth`, Lido returns only 95 ETH (post-slash). `_sendEthToDepositPool` subtracts the actual ETH received:

```solidity
if (ethValueInWithdrawal > _amount) {
    ethValueInWithdrawal -= _amount;
} else {
    ethValueInWithdrawal = 0;
}
``` [5](#0-4) 

Result: `ethValueInWithdrawal = 100 − 95 = 5 ETH`. No stETH or ETH remains in the converter, yet `ethValueInWithdrawal` permanently reports 5 ETH of phantom TVL. There is no admin function to zero this out directly.

**Step 5 — Permanent rsETHPrice inflation.**

`rsETHPrice = (totalETHInProtocol − fee) / rsethSupply` is permanently inflated by the phantom 5 ETH. [6](#0-5) 

New depositors receive fewer rsETH than they should. Existing holders cannot redeem the phantom 5 ETH because it does not exist. The yield that should have been absorbed as a loss is instead locked as phantom TVL.

**Why `ILido.sharesOf` is relevant.**

`ILido.sharesOf` is declared in the interface but never used in accounting: [7](#0-6) 

Shares are rebase-invariant. If the converter tracked stETH by shares and computed current value dynamically (`shares * getPooledEthByShares`), the accounting would remain accurate through any rebase. The current design of snapshotting a token-amount-based ETH value is fundamentally incompatible with rebasing tokens.

---

### Impact Explanation

After a Lido slashing event with stETH in the converter, a permanent phantom ETH value accumulates in `ethValueInWithdrawal`. This permanently inflates `rsETHPrice`, causing:
- New depositors to receive fewer rsETH than the actual backing warrants.
- Existing rsETH holders to be unable to claim the phantom yield (it does not exist on-chain).

This constitutes **permanent freezing of unclaimed yield** for existing rsETH holders.

---

### Likelihood Explanation

- Lido slashing events are rare but have occurred historically.
- stETH is a supported asset and `transferAssetFromDepositPool` is a routine operational call made by the Asset Transfer Role.
- No attacker action is required; the phantom residual arises automatically from the normal unstake-claim cycle following any negative rebase while stETH is in the converter.
- The phantom residual is proportional to `slash_percentage × stETH_amount_in_converter`, which can be material at scale.

---

### Recommendation

Replace the snapshot-based `ethValueInWithdrawal` accounting for stETH with a share-based approach:

1. When stETH enters the converter, record the number of **shares** (via `ILido.sharesOf` or the return value of `transferShares`).
2. When computing `ethLyingInConverter`, dynamically compute `shares × getPooledEthByShares(1e18) / 1e18` to get the current ETH value, which automatically reflects any rebase.
3. When stETH is unstaked, subtract the corresponding shares from the tracked total.

Alternatively, when `unstakeStEth` is called, update `ethValueInWithdrawal` using the **current** oracle price of the stETH being unstaked (not the original snapshot price), so the residual after claiming reflects actual ETH received.

---

### Proof of Concept

```
// Fork test outline (Mainnet fork, Lido stETH)
// 1. transferAssetFromDepositPool(stETH, 100e18)
//    → ethValueInWithdrawal = 100e18 (at oracle price ~1e18)
// 2. Simulate Lido slash: vm.store(stETH, totalSharesSlot, reducedShares)
//    → stETH.balanceOf(converter) drops to ~95e18
// 3. updateRSETHPrice()
//    → assert rsETHPrice > (actual_backing / rsethSupply)
// 4. unstakeStEth(95e18); claimStEth(requestId, hint)
//    → ETH received = 95e18
//    → ethValueInWithdrawal = 100e18 - 95e18 = 5e18
// 5. assert converter.ethValueInWithdrawal() == 5e18
//    assert stETH.balanceOf(converter) == 0
//    assert address(converter).balance == 0
// 6. updateRSETHPrice()
//    → assert rsETHPrice inflated by 5e18 / rsethSupply permanently
```

### Citations

**File:** contracts/LRTConverter.sol (L140-140)
```text
        ethValueInWithdrawal += (_amount * lrtOracle.getAssetPrice(_asset)) / 1e18;
```

**File:** contracts/LRTConverter.sol (L255-259)
```text
        if (ethValueInWithdrawal > _amount) {
            ethValueInWithdrawal -= _amount;
        } else {
            ethValueInWithdrawal = 0;
        }
```

**File:** contracts/LRTDepositPool.sol (L460-460)
```text
        assetLyingInConverter = 0; // assets in converter are accounted in their eth value => getETHDistributionData()
```

**File:** contracts/LRTDepositPool.sol (L498-499)
```text
        address lrtConverter = lrtConfig.getContract(LRTConstants.LRT_CONVERTER);
        ethLyingInConverter = ILRTConverter(lrtConverter).ethValueInWithdrawal();
```

**File:** contracts/LRTOracle.sol (L250-250)
```text
        uint256 newRsETHPrice = (totalETHInProtocol - protocolFeeInETH).divWad(rsethSupply);
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

**File:** contracts/external/lido/ILido.sol (L8-8)
```text
    function sharesOf(address _account) external view returns (uint256);
```
