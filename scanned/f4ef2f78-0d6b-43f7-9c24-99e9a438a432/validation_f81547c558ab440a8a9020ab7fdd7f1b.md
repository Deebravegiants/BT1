### Title
`stakedButUnverifiedNativeETH` Does Not Account for Pre-Verification Beacon Chain Slashing, Causing TVL Overstatement and Protocol Pause - (`contracts/NodeDelegator.sol`)

---

### Summary

`NodeDelegator.stakedButUnverifiedNativeETH` is incremented by exactly 32 ETH on `stake32Eth` and decremented by exactly 32 ETH on `verifyWithdrawalCredentials`, with no mechanism to reflect beacon chain balance reductions that occur in the window between the two calls. If a validator is slashed before credentials are verified, `getEffectivePodShares()` overstates recoverable ETH by the slash amount. This inflates protocol TVL, inflates `rsETHPrice`, causes phantom protocol-fee rsETH to be minted, and — when the slash is eventually corrected via `verifyWithdrawalCredentials` — causes a sudden price drop that can trigger the automatic pause of deposits and withdrawals.

---

### Finding Description

**Step 1 — `stake32Eth` increments the counter unconditionally.** [1](#0-0) 

`stakedButUnverifiedNativeETH += 32 ether` is the only write path that increases the variable. There is no corresponding decrease until `verifyWithdrawalCredentials` is called.

**Step 2 — `getEffectivePodShares()` sums the counter with EigenLayer withdrawable shares.** [2](#0-1) 

Before `verifyWithdrawalCredentials` is called, `withdrawableShare == 0` (no EigenLayer shares have been awarded yet). So `getEffectivePodShares()` returns exactly `stakedButUnverifiedNativeETH`, i.e., 32 ETH per unverified validator, regardless of the validator's actual beacon chain balance.

**Step 3 — `getETHDistributionData` feeds this value into TVL.** [3](#0-2) 

`ethStakedInEigenLayer` accumulates `getEffectivePodShares()` for every NDC. This feeds `getTotalAssetDeposits(ETH)`, which feeds `_getTotalEthInProtocol()` in `LRTOracle`.

**Step 4 — `_updateRsETHPrice()` uses the inflated TVL.** [4](#0-3) 

`totalETHInProtocol` is inflated by `slash_amount`. `newRsETHPrice` is therefore inflated. If `totalETHInProtocol > previousTVL`, the protocol also mints fee rsETH on the phantom "reward": [5](#0-4) 

**Step 5 — `verifyWithdrawalCredentials` decrements by exactly 32 ETH, not the post-slash balance.** [6](#0-5) 

EigenLayer's `eigenPod.verifyWithdrawalCredentials` awards shares equal to the validator's current effective balance (post-slash, e.g., 28 ETH). `stakedButUnverifiedNativeETH` is reduced by 32 ETH. Net result: `getEffectivePodShares()` drops from 32 ETH to 28 ETH — a sudden `slash_amount` reduction in reported TVL.

**Step 6 — The price drop can trigger the automatic pause.** [7](#0-6) 

If the TVL correction causes `newRsETHPrice` to fall more than `pricePercentageLimit` below `highestRsethPrice`, `LRTDepositPool`, `LRTWithdrawalManager`, and `LRTOracle` are all paused atomically. Deposits and withdrawals are blocked until an admin manually unpauses.

---

### Impact Explanation

**Primary — Medium: Temporary freezing of funds.**
A beacon chain slash of sufficient magnitude (relative to `pricePercentageLimit`) during the pre-verification window causes the automatic pause to trigger when `verifyWithdrawalCredentials` is eventually called and `updateRSETHPrice()` is invoked. All user deposits and withdrawals are blocked until admin intervention.

**Secondary — High: Theft of unclaimed yield.**
During the overstatement window, `_updateRsETHPrice()` may observe `totalETHInProtocol > previousTVL` and mint protocol-fee rsETH against the phantom `slash_amount` ETH. This fee rsETH is permanently unbacked; it dilutes all existing rsETH holders by the fee percentage of the slash amount.

**Tertiary — Low: Contract fails to deliver promised returns.**
Depositors who mint rsETH during the overstatement window pay a premium (they receive fewer rsETH than the actual backing warrants). When the price corrects downward, their rsETH is worth less ETH than they deposited.

The "permanent freezing" framing in the question is overstated: the pause is admin-reversible. The concrete scoped impacts are temporary freezing (Medium) and theft of unclaimed yield (High).

---

### Likelihood Explanation

- The pre-verification window is operator-controlled and can span days to weeks.
- Beacon chain slashings are rare but historically occur (e.g., correlated slashing events).
- No attacker action is required — a routine beacon chain slash during the window is sufficient.
- The operator has no on-chain incentive to call `verifyWithdrawalCredentials` quickly after a slash; in fact, a delayed call maximizes the overstatement window.
- Likelihood: **Low-to-Medium** (depends on slash frequency and window duration).

---

### Recommendation

1. **Introduce a `reduceUnverifiedStake(uint256 amount)` function** callable by `onlyLRTOperator` that decrements `stakedButUnverifiedNativeETH` by a proven slash amount, allowing the TVL to be corrected before `verifyWithdrawalCredentials` is called.
2. **Alternatively**, when `verifyWithdrawalCredentials` is called, compute the actual awarded shares from EigenLayer and decrement `stakedButUnverifiedNativeETH` by the awarded amount rather than a fixed 32 ETH.
3. **At minimum**, document the known overstatement window and ensure `updateRSETHPrice()` is not called between `stake32Eth` and `verifyWithdrawalCredentials` for any slashed validator.

---

### Proof of Concept

```
State: protocol has 100 ETH TVL, 100 rsETH supply → rsETHPrice = 1e18

1. operator calls stake32Eth(pubkey, sig, root)
   → stakedButUnverifiedNativeETH = 32e18
   → getEffectivePodShares() = 32e18
   → getTotalAssetDeposits(ETH) = 132e18

2. updateRSETHPrice() called
   → totalETHInProtocol = 132e18
   → previousTVL = 100e18 (100 rsETH × 1e18)
   → rewardAmount = 32e18 (phantom "reward")
   → protocolFeeInETH = 32e18 × feeBPS / 10000  ← minted on phantom ETH
   → newRsETHPrice = (132e18 - fee) / 100 ≈ 1.32e18
   → highestRsethPrice = 1.32e18

3. [beacon chain slash: validator balance drops to 28 ETH]
   → stakedButUnverifiedNativeETH still = 32e18 (no on-chain update)
   → getEffectivePodShares() still = 32e18

4. operator calls verifyWithdrawalCredentials(...)
   → stakedButUnverifiedNativeETH -= 32e18 → 0
   → EigenLayer awards shares for 28 ETH (post-slash effective balance)
   → withdrawableShare = 28e18
   → getEffectivePodShares() = 28e18
   → getTotalAssetDeposits(ETH) = 128e18

5. updateRSETHPrice() called
   → totalETHInProtocol = 128e18
   → newRsETHPrice = 128e18 / (100 + fee_rsETH_minted) ≈ 1.27e18
   → diff = 1.32e18 - 1.27e18 = 0.05e18
   → if pricePercentageLimit = 3% (3e16):
       diff (5%) > 3% × 1.32e18 → isPriceDecreaseOffLimit = true
       → LRTDepositPool.pause(), LRTWithdrawalManager.pause(), LRTOracle._pause()
       → all deposits and withdrawals blocked

Assert: getEffectivePodShares() (32e18 at step 3) > actual recoverable ETH (28e18) ✓
Assert: protocol fee rsETH minted on phantom 32e18 "reward" at step 2 ✓
Assert: protocol paused at step 5 due to slash correction ✓
```

### Citations

**File:** contracts/NodeDelegator.sol (L165-168)
```text
        // tracks staked but unverified native ETH
        stakedButUnverifiedNativeETH += 32 ether;

        _getEigenPodManager().stake{ value: 32 ether }(pubkey, signature, depositDataRoot);
```

**File:** contracts/NodeDelegator.sol (L239-244)
```text
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
