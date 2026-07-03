### Title
Stale Oracle-Snapshot in `LRTConverter.ethValueInWithdrawal` Causes rsETH Price Mis-accounting — (File: contracts/LRTConverter.sol)

---

### Summary
`LRTConverter.ethValueInWithdrawal` is stamped with the oracle price **at the moment assets are transferred into the converter**, not the current oracle price. Because `getAssetDistributionData` hard-codes `assetLyingInConverter = 0` for every LST, the converter's holdings are **exclusively** represented by this stale snapshot in `getETHDistributionData → ethLyingInConverter`. Any subsequent oracle price movement causes the protocol to mis-value those assets when computing the rsETH price.

---

### Finding Description

`transferAssetFromDepositPool` records the ETH value of incoming LSTs at the current oracle price: [1](#0-0) 

```solidity
ethValueInWithdrawal += (_amount * lrtOracle.getAssetPrice(_asset)) / 1e18;
IERC20(_asset).safeTransferFrom(lrtDepositPoolAddress, address(this), _amount);
```

From this point forward the LST balance sits in the converter, but `getAssetDistributionData` deliberately zeroes out the converter's contribution for every LST: [2](#0-1) 

```solidity
assetLyingInConverter = 0; // assets in converter are accounted in their eth value => getETHDistributionData()
```

The only place those assets are counted is `getETHDistributionData`, which reads the stale snapshot: [3](#0-2) 

```solidity
address lrtConverter = lrtConfig.getContract(LRTConstants.LRT_CONVERTER);
ethLyingInConverter = ILRTConverter(lrtConverter).ethValueInWithdrawal();
```

`_getTotalEthInProtocol` in `LRTOracle` sums all asset deposits (including this ETH figure) to derive the rsETH price: [4](#0-3) 

If the oracle price of the LST moves between the transfer call and the next `updateRSETHPrice` call, `ethValueInWithdrawal` no longer matches the true ETH value of the assets held in the converter, producing a mis-priced rsETH.

---

### Impact Explanation

**Low — Contract fails to deliver promised returns, but doesn't lose value.**

- If the LST oracle price **rises** after transfer: `ethValueInWithdrawal` underestimates the converter's holdings → `_getTotalEthInProtocol` is too low → rsETH price is understated → new depositors receive more rsETH than warranted, diluting existing holders.
- If the LST oracle price **falls** after transfer: the reverse holds — rsETH price is overstated, new depositors receive fewer rsETH than warranted.

The magnitude is bounded by the oracle price movement during the converter's holding period and the volume of assets in transit.

---

### Likelihood Explanation

**Low-to-Medium.** The operator routinely calls `transferAssetFromDepositPool` as part of normal LST-to-ETH conversion operations. LST oracle prices (e.g., stETH) drift continuously with Lido rewards. The mis-accounting persists for the entire duration between the transfer and the eventual `claimStEth` / `_sendEthToDepositPool` call, which can span days. Any caller can invoke the public `updateRSETHPrice()` during this window, materialising the stale price into the stored `rsETHPrice`.

---

### Recommendation

Replace the static snapshot with a live calculation. Track the raw asset amounts deposited into the converter per asset, and compute their current ETH value on-the-fly inside `getETHDistributionData` using the current oracle price — mirroring how `getAssetDistributionData` values LSTs held in the deposit pool and NDCs.

---

### Proof of Concept

1. Deposit pool holds 10 000 stETH; stETH oracle price = 1.00 ETH.
2. Operator calls `transferAssetFromDepositPool(stETH, 10_000)`.
   - `ethValueInWithdrawal` is set to `10_000 * 1.00 = 10_000`.
   - stETH balance in deposit pool drops to 0; `assetLyingInConverter` is always 0.
3. Lido distributes rewards; stETH oracle price rises to 1.05 ETH.
4. Any user calls `updateRSETHPrice()`.
   - `_getTotalEthInProtocol` iterates supported assets:
     - stETH contribution: `0 * 1.05 = 0` (none in pool/NDCs, converter zeroed out).
     - ETH contribution includes `ethLyingInConverter = 10_000` (stale snapshot).
   - Actual ETH value of the 10 000 stETH in the converter = `10_000 * 1.05 = 10_500 ETH`.
   - Protocol under-reports 500 ETH of value.
5. rsETH price is computed lower than it should be; new depositors are minted excess rsETH at the expense of existing holders.

### Citations

**File:** contracts/LRTConverter.sol (L140-142)
```text
        ethValueInWithdrawal += (_amount * lrtOracle.getAssetPrice(_asset)) / 1e18;

        IERC20(_asset).safeTransferFrom(lrtDepositPoolAddress, address(this), _amount);
```

**File:** contracts/LRTDepositPool.sol (L460-461)
```text
        assetLyingInConverter = 0; // assets in converter are accounted in their eth value => getETHDistributionData()
        assetLyingUnstakingVault = IERC20(asset).balanceOf(lrtUnstakingVault);
```

**File:** contracts/LRTDepositPool.sol (L498-499)
```text
        address lrtConverter = lrtConfig.getContract(LRTConstants.LRT_CONVERTER);
        ethLyingInConverter = ILRTConverter(lrtConverter).ethValueInWithdrawal();
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
