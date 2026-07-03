### Title
`stakedButUnverifiedNativeETH` Never Adjusted for Pre-Verification Beacon-Chain Slashing, Permanently Overstating TVL and Inflating rsETH Price — (`contracts/NodeDelegator.sol`)

---

### Summary

`NodeDelegator.getEffectivePodShares()` sums `stakedButUnverifiedNativeETH` (always a multiple of 32 ETH) with EigenLayer's `withdrawableShare`. When a validator is slashed on the beacon chain **before** `verifyWithdrawalCredentials` is called, the actual EigenPod balance is less than 32 ETH, but `stakedButUnverifiedNativeETH` is never reduced. The overstatement flows into `LRTOracle._updateRsETHPrice()` via the permissionless `updateRSETHPrice()`, inflating the rsETH price. A holder who redeems rsETH at this inflated price extracts more ETH than their proportional share, with the loss borne by remaining holders when the true balance is eventually reflected.

---

### Finding Description

**Root cause — `stake32Eth` increments but nothing decrements before verification:** [1](#0-0) 

`stakedButUnverifiedNativeETH` is only ever decremented inside `verifyWithdrawalCredentials`: [2](#0-1) 

There is no code path that reduces `stakedButUnverifiedNativeETH` when a beacon-chain slash occurs before credentials are verified. The variable simply holds `32 ether × N` regardless of the actual on-chain validator balance.

**TVL propagation:**

`getEffectivePodShares()` returns the sum unconditionally: [3](#0-2) 

`getETHDistributionData()` aggregates this across all NDCs: [4](#0-3) 

`getTotalAssetDeposits(ETH)` feeds into `_getTotalEthInProtocol()`: [5](#0-4) 

**Permissionless price update:**

`updateRSETHPrice()` has no access control — anyone can call it: [6](#0-5) 

The new price is computed directly from the overstated TVL: [7](#0-6) 

**Redemption at inflated price:**

`instantWithdrawal` uses the current (inflated) `rsETHPrice` at execution time: [8](#0-7) 

`getExpectedAssetAmount` multiplies rsETH amount by the inflated price: [9](#0-8) 

---

### Impact Explanation

When a validator is slashed (e.g., initial penalty ~1 ETH on a 32 ETH validator), `stakedButUnverifiedNativeETH` still counts 32 ETH. The rsETH price is inflated by `slashingLoss / rsETHSupply`. An attacker who holds rsETH redeems at this inflated rate, receiving more ETH than their proportional share. The deficit materialises for remaining holders when `verifyWithdrawalCredentials` is eventually called and EigenLayer awards shares only for the actual (slashed) effective balance — at that point the TVL drops and the rsETH price corrects downward. The attacker has extracted yield/principal that belongs to other depositors.

**Impact: High — Theft of unclaimed yield.**

---

### Likelihood Explanation

- Beacon-chain slashings are rare but real production events.
- The window between `stake32Eth` and `verifyWithdrawalCredentials` is typically days to weeks.
- `updateRSETHPrice()` is permissionless; the attacker triggers it themselves.
- `instantWithdrawal` is a supported production path requiring no operator involvement.
- The `pricePercentageLimit` upside guard may block very large price jumps, but a typical initial slashing penalty (~1–2 ETH on 32 ETH) produces a small percentage increase that is unlikely to exceed the configured threshold, especially if the protocol has accumulated legitimate yield.
- No admin compromise is required.

---

### Recommendation

When `verifyWithdrawalCredentials` is called, EigenLayer awards shares equal to the validator's **effective balance** (which may be less than 32 ETH after slashing). The protocol should reduce `stakedButUnverifiedNativeETH` by 32 ETH and add back only the actual awarded shares. One approach:

1. Read `podOwnerDepositShares` from `IEigenPodManager` before and after calling `eigenPod.verifyWithdrawalCredentials`.
2. Replace the flat `stakedButUnverifiedNativeETH -= validatorFields.length * 32 ether` with `stakedButUnverifiedNativeETH -= 32 ether * count` **and** add the delta of awarded shares to a separate verified-shares counter, so `getEffectivePodShares()` reflects reality immediately.

Alternatively, add an operator-callable function to write down `stakedButUnverifiedNativeETH` by a proven slashing amount (with a beacon proof), so the TVL can be corrected before `verifyWithdrawalCredentials` is called.

---

### Proof of Concept

```solidity
// Fork test (Holesky or mainnet fork)
// 1. Deploy/use existing NodeDelegator; call stake32Eth for one validator.
//    stakedButUnverifiedNativeETH == 32 ether.
// 2. Mock EigenPodManager.getWithdrawableShares to return 0
//    (credentials not yet verified → no EigenLayer shares).
// 3. Simulate beacon-chain slash: validator effective balance drops to 30 ether.
//    stakedButUnverifiedNativeETH is still 32 ether — no on-chain update.
// 4. Call getEffectivePodShares():
//    returns 32 ether  (should be 30 ether → 2 ether overstatement).
// 5. Call LRTOracle.updateRSETHPrice() as the attacker (no role required).
//    rsETHPrice is now inflated by 2 ether / rsETHSupply.
// 6. Attacker calls LRTWithdrawalManager.instantWithdrawal(ETH, attackerRsETH, ""):
//    receives attackerRsETH * inflatedPrice / 1e18 ETH.
// 7. Assert attacker received more ETH than deposited.
// 8. Call verifyWithdrawalCredentials (EigenLayer awards 30 ether shares).
//    stakedButUnverifiedNativeETH -= 32 ether; withdrawableShare += 30 ether.
//    Net TVL drops by 2 ether — remaining holders bear the loss.
```

### Citations

**File:** contracts/NodeDelegator.sol (L165-166)
```text
        // tracks staked but unverified native ETH
        stakedButUnverifiedNativeETH += 32 ether;
```

**File:** contracts/NodeDelegator.sol (L239-240)
```text
        // reduce the eth amount that is verified
        stakedButUnverifiedNativeETH -= (validatorFields.length * (32 ether));
```

**File:** contracts/NodeDelegator.sol (L556-562)
```text
    function getEffectivePodShares() external view override returns (uint256 ethStaked) {
        uint256 withdrawableShare =
            NodeDelegatorHelper.getWithdrawableShare(lrtConfig, IStrategy(lrtConfig.beaconChainETHStrategy()));

        // staker balances can no longer be negative
        return stakedButUnverifiedNativeETH + withdrawableShare;
    }
```

**File:** contracts/LRTDepositPool.sol (L484-492)
```text
        for (uint256 i; i < ndcsCount;) {
            ethLyingInNDCs += nodeDelegatorQueue[i].balance;

            ethStakedInEigenLayer += INodeDelegator(nodeDelegatorQueue[i]).getEffectivePodShares();
            ethUnstakingFromEigenLayer += INodeDelegator(nodeDelegatorQueue[i])
                .getAssetUnstaking(LRTConstants.ETH_TOKEN);
            unchecked {
                ++i;
            }
```

**File:** contracts/LRTOracle.sol (L87-89)
```text
    function updateRSETHPrice() public whenNotPaused {
        _updateRsETHPrice();
    }
```

**File:** contracts/LRTOracle.sol (L250-250)
```text
        uint256 newRsETHPrice = (totalETHInProtocol - protocolFeeInETH).divWad(rsethSupply);
```

**File:** contracts/LRTOracle.sol (L331-343)
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
```

**File:** contracts/LRTWithdrawalManager.sol (L228-229)
```text
        uint256 assetAmountUnlocked = getExpectedAssetAmount(asset, rsETHUnstaked);
        IRSETH(lrtConfig.rsETH()).burnFrom(address(msg.sender), rsETHUnstaked);
```

**File:** contracts/LRTWithdrawalManager.sol (L593-593)
```text
        underlyingToReceive = amount * lrtOracle.rsETHPrice() / lrtOracle.getAssetPrice(asset);
```
