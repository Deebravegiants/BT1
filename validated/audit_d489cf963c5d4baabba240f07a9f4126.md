Let me verify the exact accounting flow in `_getTotalEthInProtocol` and how `rsETHPrice` is used in minting.

### Title
Stale `ethValueInWithdrawal` Understates rsETH Price, Enabling Theft of Unclaimed Yield — (`contracts/LRTConverter.sol`, `contracts/LRTDepositPool.sol`)

---

### Summary

When stETH (a rebasing token) is transferred from the deposit pool to `LRTConverter` via `transferAssetFromDepositPool()`, the ETH value is snapshotted once into `ethValueInWithdrawal` using the oracle price at that moment. This value is never updated as stETH accrues yield. Because `getAssetDistributionData()` returns `assetLyingInConverter = 0` for non-ETH assets and delegates converter accounting entirely to `ethValueInWithdrawal` via `getETHDistributionData()`, the growing yield gap causes `_getTotalEthInProtocol()` to permanently understate TVL until the stETH is unstaked or returned. This depresses `rsETHPrice`, allowing any depositor to mint rsETH at a discount and extract the accrued yield from existing holders.

---

### Finding Description

**Step 1 — Transfer sets a stale snapshot.**

`LRTConverter.transferAssetFromDepositPool()` records the ETH value of transferred stETH once: [1](#0-0) 

```solidity
ethValueInWithdrawal += (_amount * lrtOracle.getAssetPrice(_asset)) / 1e18;
IERC20(_asset).safeTransferFrom(lrtDepositPoolAddress, address(this), _amount);
```

`ethValueInWithdrawal` is never updated again to reflect stETH's rebasing yield.

**Step 2 — Non-ETH assets in the converter are zeroed out.**

`getAssetDistributionData()` explicitly sets the converter contribution to zero for stETH and all other LSTs, with a comment that they are accounted for via `getETHDistributionData()`: [2](#0-1) 

```solidity
assetLyingInConverter = 0; // assets in converter are accounted in their eth value => getETHDistributionData()
```

**Step 3 — ETH accounting reads the stale snapshot.**

`getETHDistributionData()` reads `ethValueInWithdrawal` directly: [3](#0-2) 

```solidity
address lrtConverter = lrtConfig.getContract(LRTConstants.LRT_CONVERTER);
ethLyingInConverter = ILRTConverter(lrtConverter).ethValueInWithdrawal();
```

**Step 4 — Oracle price computation uses the understated TVL.**

`_getTotalEthInProtocol()` sums `getTotalAssetDeposits(asset) * assetPrice` for every supported asset: [4](#0-3) 

For ETH, `getTotalAssetDeposits(ETH_TOKEN)` returns `ethLyingInConverter` = stale `ethValueInWithdrawal`. For stETH, `getTotalAssetDeposits(stETH)` returns `assetLyingInConverter = 0`. The yield that accrued on stETH in the converter is counted in neither leg.

**Step 5 — rsETHPrice is set below fair value.** [5](#0-4) 

```solidity
uint256 newRsETHPrice = (totalETHInProtocol - protocolFeeInETH).divWad(rsethSupply);
```

With `totalETHInProtocol` understated by the accrued stETH yield, `rsETHPrice` is set below its fair value.

**Step 6 — Attacker mints rsETH at a discount.**

`getRsETHAmountToMint` divides by the stale (depressed) `rsETHPrice`: [6](#0-5) 

```solidity
rsethAmountToMint = (amount * lrtOracle.getAssetPrice(asset)) / lrtOracle.rsETHPrice();
```

`lrtOracle.getAssetPrice(stETH)` returns the current (higher) oracle price, while `lrtOracle.rsETHPrice()` is the stored understated value. The attacker receives more rsETH than the fair share, diluting existing holders by exactly the yield gap.

---

### Impact Explanation

Every unit of stETH yield that accrues while stETH sits in `LRTConverter` is invisible to the TVL calculation. When `updateRSETHPrice()` is called, `rsETHPrice` is set lower than the true per-share value. Any depositor — including a deliberate attacker — who deposits stETH (or any asset) between oracle updates captures a portion of that yield gap as excess rsETH. Existing rsETH holders bear the loss. This is a direct, permissionless theft of unclaimed yield proportional to: `(stETH_amount_in_converter × yield_rate × time_elapsed)`.

**Impact: High — Theft of unclaimed yield.**

---

### Likelihood Explanation

- `transferAssetFromDepositPool` is a routine operator action (role-gated, but expected to be called regularly as part of the unstaking workflow).
- stETH accrues yield continuously (~3–4% APR); the gap grows with every block.
- `depositAsset` is fully permissionless — any address can exploit the depressed price immediately after `updateRSETHPrice()` is called.
- No front-running, brute force, or admin compromise is required.

**Likelihood: High.**

---

### Recommendation

Replace the static snapshot with a live valuation. In `getETHDistributionData()`, instead of reading `ethValueInWithdrawal`, query the converter's actual LST balances and price them at the current oracle rate:

```solidity
// pseudocode
for each supported LST asset:
    uint256 bal = IERC20(asset).balanceOf(lrtConverter);
    ethLyingInConverter += (bal * lrtOracle.getAssetPrice(asset)) / 1e18;
```

Alternatively, update `ethValueInWithdrawal` on every `updateRSETHPrice()` call by re-pricing the converter's current LST balances. The static snapshot pattern is fundamentally incompatible with rebasing tokens.

---

### Proof of Concept

```solidity
// Fork test (Mainnet fork, block after stETH transfer to converter)
function test_staleConverterYieldTheft() public {
    // 1. Operator transfers 100 stETH to converter at oracle price P0
    vm.prank(assetTransferRole);
    lrtConverter.transferAssetFromDepositPool(stETH, 100e18);
    // ethValueInWithdrawal = 100e18 * P0 / 1e18

    // 2. Advance ~30 days; stETH rebases, oracle price rises to P1 > P0
    vm.warp(block.timestamp + 30 days);
    // stETH.balanceOf(converter) is now worth 100e18 * P1 / 1e18 in ETH
    // but ethValueInWithdrawal is still 100e18 * P0 / 1e18

    // 3. Oracle update — rsETHPrice is set using understated TVL
    lrtOracle.updateRSETHPrice();
    uint256 depressedPrice = lrtOracle.rsETHPrice();

    // 4. Attacker deposits 1 stETH at depressed price
    uint256 rsethMinted = lrtDepositPool.getRsETHAmountToMint(stETH, 1e18);
    // rsethMinted = (1e18 * P1) / depressedPrice > fair_amount

    // 5. Assert: attacker received more rsETH than fair
    uint256 fairAmount = (1e18 * P1) / fairRsETHPrice; // fairRsETHPrice uses P1 for converter
    assertGt(rsethMinted, fairAmount);

    // 6. Assert: ethValueInWithdrawal < actual ETH value of stETH in converter
    uint256 actualValue = (IERC20(stETH).balanceOf(address(lrtConverter)) * lrtOracle.getAssetPrice(stETH)) / 1e18;
    assertLt(lrtConverter.ethValueInWithdrawal(), actualValue);
}
```

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

**File:** contracts/LRTDepositPool.sol (L498-500)
```text
        address lrtConverter = lrtConfig.getContract(LRTConstants.LRT_CONVERTER);
        ethLyingInConverter = ILRTConverter(lrtConverter).ethValueInWithdrawal();
    }
```

**File:** contracts/LRTDepositPool.sol (L520-520)
```text
        rsethAmountToMint = (amount * lrtOracle.getAssetPrice(asset)) / lrtOracle.rsETHPrice();
```

**File:** contracts/LRTOracle.sol (L250-250)
```text
        uint256 newRsETHPrice = (totalETHInProtocol - protocolFeeInETH).divWad(rsethSupply);
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
