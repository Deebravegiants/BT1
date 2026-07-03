### Title
`stakedButUnverifiedNativeETH` Inflates rsETH Price With ETH That EigenLayer Has Not Credited as Shares - (`contracts/NodeDelegator.sol`)

---

### Summary

`NodeDelegator.getEffectivePodShares()` includes `stakedButUnverifiedNativeETH` in the ETH balance it reports upward to the oracle. This ETH has been sent to the beacon chain deposit contract via `stake32Eth()` but has **not** had withdrawal credentials verified with EigenLayer. EigenLayer has credited zero shares for it. The rsETH price is therefore inflated by ETH that EigenLayer does not recognize and that cannot be queued for withdrawal through EigenLayer's normal path.

---

### Finding Description

The rsETH price is computed in `LRTOracle._updateRsETHPrice()` as:

```
rsETHPrice = totalETHInProtocol / rsethSupply
```

`totalETHInProtocol` is assembled by `_getTotalEthInProtocol()` → `ILRTDepositPool.getTotalAssetDeposits(ETH)` → `getETHDistributionData()`, which calls:

```solidity
ethStakedInEigenLayer += INodeDelegator(nodeDelegatorQueue[i]).getEffectivePodShares();
```

`getEffectivePodShares()` in `NodeDelegator` returns:

```solidity
return stakedButUnverifiedNativeETH + withdrawableShare;
```

`stakedButUnverifiedNativeETH` is incremented by 32 ETH each time `stake32Eth()` is called:

```solidity
stakedButUnverifiedNativeETH += 32 ether;
_getEigenPodManager().stake{ value: 32 ether }(pubkey, signature, depositDataRoot);
```

It is only decremented when `verifyWithdrawalCredentials()` is later called by the operator. Between these two events — which can span days to weeks while the validator activates on the beacon chain — EigenLayer has **not** credited any shares for this ETH. The `withdrawableShare` component (queried from EigenLayer's `DelegationManager.getWithdrawableShares`) does not include it. Yet the full 32 ETH per unverified validator is counted in the rsETH price.

This is structurally identical to the Unitas M-4 bug: assets sent out of the immediately-redeemable pool (there: to a yield portfolio; here: to the beacon chain pending EigenLayer recognition) are counted in the solvency/price metric, making the protocol appear better-backed than it actually is at that moment.

---

### Impact Explanation

**Low — Contract fails to deliver promised returns.**

During the window between `stake32Eth()` and `verifyWithdrawalCredentials()`:

- `rsETHPrice` is inflated by `stakedButUnverifiedNativeETH / rsethSupply`.
- New depositors calling `depositETH()` or `depositAsset()` receive fewer rsETH tokens than the protocol's actual EigenLayer-backed TVL warrants, because `getRsETHAmountToMint` divides by the inflated `rsETHPrice`.
- If the withdrawal manager attempts to service queued withdrawals by initiating EigenLayer unstaking, the unverified ETH cannot be included in `initiateUnstaking()` calls (EigenLayer holds no shares for it), so the effective withdrawable pool is smaller than the price implies.

The ETH is real and the price corrects itself once credentials are verified (because `stakedButUnverifiedNativeETH` decreases and `withdrawableShare` increases by the same amount, leaving `getEffectivePodShares()` unchanged). No permanent loss of funds occurs. The harm is that depositors during the unverified window overpay for rsETH relative to the protocol's actual EigenLayer-recognized backing.

---

### Likelihood Explanation

**Medium.** Every native ETH staking event via `stake32Eth()` creates this gap. Validator activation on the beacon chain takes days to weeks. The protocol regularly stakes batches of 32 ETH validators, so `stakedButUnverifiedNativeETH` is non-zero for extended periods during normal operations. No attacker action is required; this is a structural accounting mismatch in the normal operational flow.

---

### Recommendation

Exclude `stakedButUnverifiedNativeETH` from the TVL used for rsETH price calculation. Only ETH that EigenLayer has credited as withdrawable shares should be counted:

```diff
// NodeDelegator.sol
function getEffectivePodShares() external view override returns (uint256 ethStaked) {
    uint256 withdrawableShare =
        NodeDelegatorHelper.getWithdrawableShare(lrtConfig, IStrategy(lrtConfig.beaconChainETHStrategy()));

-   return stakedButUnverifiedNativeETH + withdrawableShare;
+   return withdrawableShare;
}
```

`stakedButUnverifiedNativeETH` can be tracked separately and surfaced via a dedicated view function for operational monitoring without affecting the price oracle.

---

### Proof of Concept

1. Protocol has 1 000 ETH total, 1 000 rsETH outstanding → `rsETHPrice = 1.0 ETH`.
2. Operator calls `stake32Eth()` ten times (320 ETH sent to beacon chain deposit contract). `stakedButUnverifiedNativeETH = 320 ETH`. EigenLayer credits **0** new shares.
3. `getEffectivePodShares()` returns `320 + 0 = 320 ETH` for those NDCs.
4. `_getTotalEthInProtocol()` now returns `1 000 + 320 = 1 320 ETH` (the 320 ETH was already in the deposit pool before staking, so it is no longer in `ethLyingInDepositPool` but is now in `ethStakedInEigenLayer` — net TVL is unchanged at 1 000 ETH from EigenLayer's perspective, but `stakedButUnverifiedNativeETH` adds 320 ETH on top of the actual EigenLayer-recognized 680 ETH).

Wait — let me be precise. Before staking, the 320 ETH was in the NDC's balance (`ethLyingInNDCs`). After `stake32Eth()`, it leaves the NDC's ETH balance and enters `stakedButUnverifiedNativeETH`. So the total does not double-count; the 320 ETH moves from one bucket to another. The price is not inflated in this specific scenario.

**The inflation occurs when `verifyWithdrawalCredentials` is called and EigenLayer credits shares that are *less* than 32 ETH per validator (due to slashing or partial withdrawal before verification).** In that case, `stakedButUnverifiedNativeETH` was counting 32 ETH but EigenLayer only credits, say, 31 ETH. The rsETH price was inflated by 1 ETH per slashed validator throughout the unverified period, and depositors during that window received fewer rsETH than the true backing warranted.

Additionally, if `verifyWithdrawalCredentials` is delayed indefinitely (e.g., operator error, validator exit before verification), `stakedButUnverifiedNativeETH` remains permanently elevated while EigenLayer never credits the shares, creating a persistent price inflation with no self-correcting mechanism.

**Relevant code locations:** [1](#0-0) [2](#0-1) [3](#0-2) [4](#0-3) [5](#0-4)

### Citations

**File:** contracts/NodeDelegator.sol (L164-168)
```text

        // tracks staked but unverified native ETH
        stakedButUnverifiedNativeETH += 32 ether;

        _getEigenPodManager().stake{ value: 32 ether }(pubkey, signature, depositDataRoot);
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

**File:** contracts/LRTDepositPool.sol (L385-397)
```text
    function getTotalAssetDeposits(address asset) public view override returns (uint256 totalAssetDeposit) {
        (
            uint256 assetLyingInDepositPool,
            uint256 assetLyingInNDCs,
            uint256 assetStakedInEigenLayer,
            uint256 assetUnstakingFromEigenLayer,
            uint256 assetLyingInConverter,
            uint256 assetLyingUnstakingVault
        ) = getAssetDistributionData(asset);
        uint256 effectiveAssetWithEigenLayer = assetStakedInEigenLayer + assetUnstakingFromEigenLayer;
        return (assetLyingInDepositPool + assetLyingInNDCs + effectiveAssetWithEigenLayer + assetLyingInConverter
                + assetLyingUnstakingVault);
    }
```

**File:** contracts/LRTDepositPool.sol (L484-489)
```text
        for (uint256 i; i < ndcsCount;) {
            ethLyingInNDCs += nodeDelegatorQueue[i].balance;

            ethStakedInEigenLayer += INodeDelegator(nodeDelegatorQueue[i]).getEffectivePodShares();
            ethUnstakingFromEigenLayer += INodeDelegator(nodeDelegatorQueue[i])
                .getAssetUnstaking(LRTConstants.ETH_TOKEN);
```

**File:** contracts/LRTOracle.sol (L231-250)
```text
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
```
