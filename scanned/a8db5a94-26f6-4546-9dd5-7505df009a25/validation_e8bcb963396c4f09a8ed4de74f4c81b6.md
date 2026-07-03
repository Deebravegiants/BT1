### Title
Permanently inflated `stakedButUnverifiedNativeETH` after beacon-chain slashing of unverified validators causes protocol insolvency — (File: `contracts/NodeDelegator.sol`)

---

### Summary

When a validator is staked via `stake32Eth()`, `stakedButUnverifiedNativeETH` is incremented by exactly 32 ETH. The only code path that decrements it is `verifyWithdrawalCredentials()`. However, if a validator is slashed on the beacon chain **before** its withdrawal credentials are verified with EigenLayer, `verifyWithdrawalCredentials()` cannot be called (EigenPod explicitly requires that validators proven via this method must not have an exit epoch set, and slashing forces an exit epoch). This permanently traps 32 ETH in `stakedButUnverifiedNativeETH` for each such validator, inflating `getEffectivePodShares()`, `_getTotalEthInProtocol()`, and ultimately `rsETHPrice`, while the actual ETH backing is lower by the slashing penalty. The result is protocol insolvency: rsETH is backed by less ETH than the oracle claims.

---

### Finding Description

**Step 1 — Staking increments `stakedButUnverifiedNativeETH`:**

In `NodeDelegator.stake32Eth()`, every validator staked adds exactly 32 ETH to the counter: [1](#0-0) 

**Step 2 — The only decrement path is `verifyWithdrawalCredentials()`:** [2](#0-1) 

There is no other code path that decrements `stakedButUnverifiedNativeETH`.

**Step 3 — Slashed validators cannot have credentials verified:**

The EigenPod interface explicitly states:

> *"Validators proven via this method MUST NOT have an exit epoch set already."* [3](#0-2) 

Beacon-chain slashing forces an exit epoch onto the validator. Therefore, `verifyWithdrawalCredentials()` will revert for any validator slashed before its credentials were verified, and `stakedButUnverifiedNativeETH` is **never decremented** for that validator.

**Step 4 — `getEffectivePodShares()` uses the inflated counter:** [4](#0-3) 

The slashed validator contributes 32 ETH to `stakedButUnverifiedNativeETH` and 0 to `withdrawableShare` (since credentials were never verified, the EigenPod checkpoint does not credit it). The function returns 32 ETH for a validator whose actual backing is, e.g., 28 ETH — a permanent 4 ETH overstatement per slashed validator.

**Step 5 — The inflated value propagates to `rsETHPrice`:**

`LRTDepositPool.getETHDistributionData()` calls `getEffectivePodShares()` across all NodeDelegators: [5](#0-4) 

`LRTOracle._getTotalEthInProtocol()` sums all asset values including this inflated ETH figure: [6](#0-5) 

`_updateRsETHPrice()` then computes `rsETHPrice` from this inflated TVL: [7](#0-6) 

**Step 6 — Downstream minting and withdrawal use the inflated price:**

L1 deposits use `lrtOracle.rsETHPrice()` to determine how many rsETH tokens to mint: [8](#0-7) 

L2 pools use `getRate()` which ultimately reads the same inflated `rsETHPrice` propagated via `RSETHMultiChainRateProvider`: [9](#0-8) 

---

### Impact Explanation

**Critical — Protocol insolvency.**

For each validator slashed before credential verification, the protocol permanently overstates its ETH TVL by the slashing penalty (up to 1/32 of 32 ETH = ~1 ETH per validator under EIP-7251 rules, or more under severe slashing). With multiple validators, this overstatement compounds. The inflated `rsETHPrice` means:

- New depositors receive fewer rsETH tokens than the actual backing warrants (they overpay).
- Existing rsETH holders hold tokens whose oracle-claimed value exceeds the real backing.
- When withdrawals are processed at the inflated price, the protocol pays out more ETH than it actually holds, leaving later withdrawers unable to redeem at par — a classic insolvency cascade.

There is no automatic correction mechanism: `stakedButUnverifiedNativeETH` has no admin override, no checkpoint-based correction, and no decay function.

---

### Likelihood Explanation

**Medium.**

The window between `stake32Eth()` and `verifyWithdrawalCredentials()` spans multiple days (beacon chain activation queue + proof submission latency). Beacon-chain slashing events (double signing, surround voting) are rare but have occurred on mainnet. The protocol operates many validators across multiple NodeDelegators, increasing aggregate exposure. A single slashing event during the unverified window permanently corrupts the accounting with no recovery path.

---

### Recommendation

1. **Add an admin-callable correction function** that decrements `stakedButUnverifiedNativeETH` for a specific validator pubkey when it is confirmed slashed and unverifiable (e.g., by checking the EigenPod's validator status).
2. **Alternatively**, track per-validator state so that slashed-but-unverified validators can be individually zeroed out.
3. **Add a circuit breaker** in `_updateRsETHPrice()` that detects when `stakedButUnverifiedNativeETH` has not decreased over a configurable period despite checkpoint completions, and pauses the protocol.
4. **Consider using the checkpoint mechanism** to reconcile `stakedButUnverifiedNativeETH` against actual EigenPod balances periodically.

---

### Proof of Concept

1. Protocol operator calls `stake32Eth(pubkey, sig, root)` for validator V.
   - `stakedButUnverifiedNativeETH += 32 ether` → now 32 ETH.
2. Before `verifyWithdrawalCredentials()` is called, validator V is slashed on the beacon chain (e.g., double-signing). V receives an exit epoch.
3. Operator attempts `verifyWithdrawalCredentials(...)` for V → EigenPod reverts: validator has exit epoch set.
4. `stakedButUnverifiedNativeETH` remains at 32 ETH permanently. V's actual remaining balance (e.g., 28 ETH after a 4 ETH penalty) eventually arrives at the EigenPod but is not credited via `withdrawableShare` (since credentials were never verified, V is INACTIVE in EigenPod).
5. `getEffectivePodShares()` returns 32 ETH for this NDC (from `stakedButUnverifiedNativeETH`) instead of the real 28 ETH.
6. `_getTotalEthInProtocol()` is inflated by 4 ETH.
7. `updateRSETHPrice()` is called → `rsETHPrice` is computed from inflated TVL → rsETH appears worth more than it is.
8. Users who withdraw at the inflated price receive more ETH than the protocol can sustain, leaving later withdrawers unable to redeem at par.

### Citations

**File:** contracts/NodeDelegator.sol (L165-168)
```text
        // tracks staked but unverified native ETH
        stakedButUnverifiedNativeETH += 32 ether;

        _getEigenPodManager().stake{ value: 32 ether }(pubkey, signature, depositDataRoot);
```

**File:** contracts/NodeDelegator.sol (L235-244)
```text
        if (stakedButUnverifiedNativeETH < validatorFields.length * (32 ether)) {
            revert InsufficientStakedBalance();
        }

        // reduce the eth amount that is verified
        stakedButUnverifiedNativeETH -= (validatorFields.length * (32 ether));

        eigenPod.verifyWithdrawalCredentials(
            beaconTimestamp, stateRootProof, validatorIndices, validatorFieldsProofs, validatorFields
        );
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

**File:** contracts/external/eigenlayer/interfaces/IEigenPod.sol (L206-210)
```text
    function verifyWithdrawalCredentials(
        uint64 beaconTimestamp,
        BeaconChainProofs.StateRootProof calldata stateRootProof,
        uint40[] calldata validatorIndices,
        bytes[] calldata validatorFieldsProofs,
```

**File:** contracts/LRTDepositPool.sol (L484-493)
```text
        for (uint256 i; i < ndcsCount;) {
            ethLyingInNDCs += nodeDelegatorQueue[i].balance;

            ethStakedInEigenLayer += INodeDelegator(nodeDelegatorQueue[i]).getEffectivePodShares();
            ethUnstakingFromEigenLayer += INodeDelegator(nodeDelegatorQueue[i])
                .getAssetUnstaking(LRTConstants.ETH_TOKEN);
            unchecked {
                ++i;
            }
        }
```

**File:** contracts/LRTDepositPool.sol (L519-521)
```text
        // calculate rseth amount to mint based on asset amount and asset exchange rate
        rsethAmountToMint = (amount * lrtOracle.getAssetPrice(asset)) / lrtOracle.rsETHPrice();
    }
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

**File:** contracts/cross-chain/RSETHMultiChainRateProvider.sol (L26-28)
```text
    function getLatestRate() public view override returns (uint256) {
        return ILRTOracle(rsETHPriceOracle).rsETHPrice();
    }
```
