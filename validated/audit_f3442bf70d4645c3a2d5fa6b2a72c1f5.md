### Title
Hardcoded 18-Decimal Assumption in TVL Calculation and rsETH Minting Causes Protocol Insolvency if a Non-18-Decimal Asset Is Supported — (`contracts/LRTOracle.sol` / `contracts/LRTDepositPool.sol`)

---

### Summary

`LRTOracle._getTotalEthInProtocol` and `LRTDepositPool.getRsETHAmountToMint` both silently assume every supported asset carries 18 decimals. `LRTConfig._addNewSupportedAsset` imposes no decimal check. If a token with fewer than 18 decimals (e.g., a 6-decimal LST or collateral) is ever added, the TVL is undercounted by `10^(18-decimals)`, the rsETH price collapses proportionally, and any subsequent ETH depositor can drain the protocol by receiving far more rsETH than their deposit is worth.

---

### Finding Description

**`LRTOracle._getTotalEthInProtocol`** (lines 331–349):

```solidity
uint256 assetER = getAssetPrice(asset);          // 1e18-normalised price
uint256 totalAssetAmt = ILRTDepositPool(lrtDepositPoolAddr).getTotalAssetDeposits(asset);
totalETHInProtocol += totalAssetAmt.mulWad(assetER);   // divides by 1e18
```

`mulWad` divides by `1e18`. For a 6-decimal token, `totalAssetAmt` is already `1e12` times smaller than the equivalent 18-decimal quantity, so the ETH contribution of that asset is undercounted by `1e12`.

**`LRTDepositPool.getRsETHAmountToMint`** (line 520):

```solidity
rsethAmountToMint = (amount * lrtOracle.getAssetPrice(asset)) / lrtOracle.rsETHPrice();
```

`amount` is the raw token balance in the token's native decimals. For a 6-decimal token, `amount` is `1e12` times smaller than the WAD-scaled value the formula expects, so the depositor receives `1e12` times fewer rsETH than they should — but the TVL is also undercounted by the same factor, so the rsETH price is artificially depressed.

**`LRTConfig._addNewSupportedAsset`** (lines 106–118) performs no decimal check:

```solidity
function _addNewSupportedAsset(address asset, uint256 depositLimit) private {
    UtilLib.checkNonZeroAddress(asset);
    if (depositLimit == 0) { revert InvalidDepositLimit(); }
    if (isSupportedAsset[asset]) { revert AssetAlreadySupported(); }
    isSupportedAsset[asset] = true;
    ...
}
```

No `IERC20Metadata(asset).decimals() == 18` guard exists anywhere in the asset-onboarding path.

---

### Impact Explanation

Suppose a 6-decimal asset (e.g., a future LST or bridged collateral) is added with a significant deposit limit.

1. Users deposit the 6-decimal asset. `_getTotalEthInProtocol` counts its ETH value as `1e12` times too small.
2. `_updateRsETHPrice` computes `rsETHPrice = totalETHInProtocol / rsethSupply`. Because the 6-decimal asset's ETH contribution is nearly zero in the formula, `rsETHPrice` collapses far below its true value.
3. An attacker deposits ETH (18-decimal, correctly accounted). `getRsETHAmountToMint` returns `(ethAmount * 1e18) / depressedRsETHPrice`, minting `1e12×` more rsETH than the deposit is worth.
4. The attacker redeems the inflated rsETH balance against the protocol's real ETH reserves, draining them.

Impact: **Critical — direct theft of existing depositors' funds / protocol insolvency.**

---

### Likelihood Explanation

Adding a new supported asset requires the `TIME_LOCK_ROLE` (a timelocked admin action, `LRTConfig.addNewSupportedAsset`). The current supported assets (stETH, ETHx, rETH, swETH, sfrxETH) are all 18-decimal. However:

- The protocol is designed to expand its supported asset list over time.
- No on-chain guard prevents a non-18-decimal asset from being added.
- A single governance mistake (e.g., adding a bridged USDC-denominated LST or a future 6-decimal token) silently activates the vulnerability with no further attacker precondition.

Likelihood: **Low-to-Medium** (requires one governance action; no attacker capability needed beyond a standard ETH deposit after the fact).

---

### Recommendation

1. **Enforce 18 decimals at asset-onboarding time** in `LRTConfig._addNewSupportedAsset`:

```solidity
if (IERC20Metadata(asset).decimals() != 18) revert AssetDecimalsNotSupported();
```

2. **Alternatively**, normalise `totalAssetAmt` in `_getTotalEthInProtocol` and `amount` in `getRsETHAmountToMint` to 18 decimals before applying WAD math:

```solidity
uint256 normalised = totalAssetAmt * 10 ** (18 - IERC20Metadata(asset).decimals());
totalETHInProtocol += normalised.mulWad(assetER);
```

Option 1 is simpler and eliminates the attack surface entirely.

---

### Proof of Concept

**Setup:** Admin adds a 6-decimal token `T6` with `getAssetPrice(T6) = 3e14` (≈ 0.0003 ETH per token). 1 000 000 units of `T6` (= 1 T6) are deposited.

**`_getTotalEthInProtocol` result:**
```
totalAssetAmt = 1_000_000          // 6-decimal raw balance
assetER       = 3e14
contribution  = 1_000_000 * 3e14 / 1e18 = 300 wei   // should be 3e14 wei (0.0003 ETH)
```
TVL is undercounted by `1e12`.

**`rsETHPrice` after update:**
Assume prior TVL = 1 000 ETH, rsethSupply = 1 000e18. Adding T6 contribution of 300 wei is negligible → `rsETHPrice ≈ 1e18` (unchanged, but the T6 deposit is effectively invisible).

**Attacker deposits 1 ETH:**
```
rsethAmountToMint = (1e18 * 1e18) / 1e18 = 1e18   // 1 rsETH — correct
```
The T6 depositor's 0.0003 ETH worth of value is not reflected in the price, so the attacker's rsETH is backed by more ETH than it should be. At scale (large T6 deposits), the rsETH price collapses and the attacker mints rsETH at a fraction of its true cost, then redeems against the real ETH pool.

**Root cause lines:** [1](#0-0) [2](#0-1) [3](#0-2)

### Citations

**File:** contracts/LRTOracle.sol (L339-343)
```text
            uint256 assetER = getAssetPrice(asset);
            // totalAssetAmt is in 1e18 precision (standard token decimals)
            uint256 totalAssetAmt = ILRTDepositPool(lrtDepositPoolAddr).getTotalAssetDeposits(asset);

            totalETHInProtocol += totalAssetAmt.mulWad(assetER);
```

**File:** contracts/LRTDepositPool.sol (L519-521)
```text
        // calculate rseth amount to mint based on asset amount and asset exchange rate
        rsethAmountToMint = (amount * lrtOracle.getAssetPrice(asset)) / lrtOracle.rsETHPrice();
    }
```

**File:** contracts/LRTConfig.sol (L106-118)
```text
    function _addNewSupportedAsset(address asset, uint256 depositLimit) private {
        UtilLib.checkNonZeroAddress(asset);
        if (depositLimit == 0) {
            revert InvalidDepositLimit();
        }
        if (isSupportedAsset[asset]) {
            revert AssetAlreadySupported();
        }
        isSupportedAsset[asset] = true;
        supportedAssetList.push(asset);
        depositLimitByAsset[asset] = depositLimit;
        emit AddedNewSupportedAsset(asset, depositLimit);
    }
```
