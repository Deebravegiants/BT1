### Title
Permanently Inflated `stakedButUnverifiedNativeETH` After Validator Exit/Slash Before Credential Verification Overstates TVL and Dilutes Yield — (`contracts/NodeDelegator.sol`)

---

### Summary

When `stake32Eth` is called for a validator, `stakedButUnverifiedNativeETH` is incremented by 32 ETH. The only code path that decrements it is `NodeDelegator.verifyWithdrawalCredentials`. However, EigenLayer's `IEigenPod.verifyWithdrawalCredentials` enforces that validators **must not have an exit epoch set already** (`ValidatorIsExitingBeaconChain` error). If a validator exits or is slashed on the beacon chain before credential verification occurs, the call to `eigenPod.verifyWithdrawalCredentials` reverts, the entire transaction reverts, and `stakedButUnverifiedNativeETH` is never decremented. There is no admin recovery path to correct this counter. The result is a permanently inflated `getEffectivePodShares()`, which inflates TVL, causes protocol fee minting on phantom rewards, and dilutes existing rsETH holders' yield.

---

### Finding Description

**Root cause — `NodeDelegator.verifyWithdrawalCredentials` is the sole decrement path:** [1](#0-0) 

`stakedButUnverifiedNativeETH` is incremented unconditionally on every `stake32Eth` call. [2](#0-1) 

The decrement happens before the external call. If `eigenPod.verifyWithdrawalCredentials` reverts (e.g., `ValidatorIsExitingBeaconChain`), the entire transaction reverts and `stakedButUnverifiedNativeETH` is never reduced.

**EigenLayer enforces the exit-epoch restriction:** [3](#0-2) [4](#0-3) 

The NatSpec explicitly states validators with an exit epoch set cannot be verified. There is no alternative decrement path in `NodeDelegator` — no admin setter, no checkpoint hook, no recovery function for `stakedButUnverifiedNativeETH`.

**`getEffectivePodShares()` adds the stuck counter to EigenLayer withdrawable shares:** [5](#0-4) 

Since the exited validator was never verified, `withdrawableShare` from EigenLayer is 0 for it, but `stakedButUnverifiedNativeETH` still carries the full 32 ETH.

**TVL inflation propagates through the oracle:** [6](#0-5) [7](#0-6) 

`_getTotalEthInProtocol()` → `getTotalAssetDeposits(ETH)` → `getETHDistributionData()` → `getEffectivePodShares()`. The phantom 32 ETH flows directly into the rsETH price calculation.

**Protocol fee minting on phantom rewards:** [8](#0-7) [9](#0-8) 

When `updateRSETHPrice()` is called after the phantom ETH inflates `totalETHInProtocol` above `previousTVL`, the protocol computes a `rewardAmount` on non-existent ETH and mints rsETH fee tokens to the treasury. This dilutes all existing rsETH holders.

---

### Impact Explanation

- `stakedButUnverifiedNativeETH` is permanently stuck at N×32 ETH for N exited/slashed-before-verification validators.
- `getEffectivePodShares()` overstates actual ETH backing by N×32 ETH indefinitely.
- `_getTotalEthInProtocol()` is inflated, causing `newRsETHPrice` to be overstated.
- Protocol fee rsETH is minted to the treasury on phantom "rewards," directly diluting existing holders' unclaimed yield.
- New depositors receive fewer rsETH per ETH at the inflated price, compounding the harm.

---

### Likelihood Explanation

Beacon chain slashings and voluntary exits are routine events. The window between `stake32Eth` and `verifyWithdrawalCredentials` can span multiple epochs (operators batch credential proofs). Any validator that exits or is slashed during this window triggers the stuck state. No attacker action is required — this is a normal operational scenario. The stuck state is permanent because there is no recovery function.

---

### Recommendation

1. Add an admin/operator function to manually decrement `stakedButUnverifiedNativeETH` for validators that can be proven to have exited without credential verification (e.g., by providing a beacon chain proof of exit).
2. Alternatively, track per-validator state so that individual stuck entries can be cleared.
3. Consider using `verifyStaleBalance` (already in `IEigenPod`) as a trigger to initiate a checkpoint and then allow `stakedButUnverifiedNativeETH` to be corrected.

---

### Proof of Concept

```solidity
// 1. Operator calls stake32Eth for validator V
//    stakedButUnverifiedNativeETH += 32 ether  (now = 32 ETH)

// 2. Validator V exits on beacon chain (exit_epoch is set)

// 3. Operator attempts verifyWithdrawalCredentials for V
//    → eigenPod.verifyWithdrawalCredentials reverts with ValidatorIsExitingBeaconChain
//    → entire tx reverts; stakedButUnverifiedNativeETH remains 32 ETH

// 4. getEffectivePodShares() = 32 ETH + 0 (no EL shares) = 32 ETH (phantom)

// 5. LRTOracle._getTotalEthInProtocol() includes phantom 32 ETH

// 6. updateRSETHPrice():
//    totalETHInProtocol = realETH + 32 ETH (phantom)
//    rewardAmount = totalETHInProtocol - previousTVL  (includes phantom)
//    protocolFeeInETH = rewardAmount * feeBPS / 10000  (fee on phantom)
//    treasury receives rsETH minted on phantom rewards → existing holders diluted

// Assert: getEffectivePodShares() > actual ETH in pod
// Assert: rsETHPrice > (actual ETH backing / rsETH supply)
``` [10](#0-9) [11](#0-10) [5](#0-4) [8](#0-7)

### Citations

**File:** contracts/NodeDelegator.sol (L150-175)
```text
    function stake32Eth(
        bytes calldata pubkey,
        bytes calldata signature,
        bytes32 depositDataRoot
    )
        public
        whenNotPaused
        onlyLRTOperator
    {
        IPubkeyRegistry pubkeyRegistry = IPubkeyRegistry(lrtConfig.pubkeyRegistry());
        if (pubkeyRegistry.hasPubkey(pubkey)) {
            revert PubkeyAlreadyRegistered();
        }
        pubkeyRegistry.addPubkey(pubkey);

        // tracks staked but unverified native ETH
        stakedButUnverifiedNativeETH += 32 ether;

        _getEigenPodManager().stake{ value: 32 ether }(pubkey, signature, depositDataRoot);

        if (address(eigenPod) == address(0)) {
            eigenPod = _getEigenPodManager().ownerToPod(address(this));
            emit EigenPodCreated(address(eigenPod), address(this));
        }
        emit ETHStaked(pubkey, 32 ether);
    }
```

**File:** contracts/NodeDelegator.sol (L225-245)
```text
    function verifyWithdrawalCredentials(
        uint64 beaconTimestamp,
        BeaconChainProofs.StateRootProof calldata stateRootProof,
        uint40[] calldata validatorIndices,
        bytes[] calldata validatorFieldsProofs,
        bytes32[][] calldata validatorFields
    )
        external
        onlyLRTOperator
    {
        if (stakedButUnverifiedNativeETH < validatorFields.length * (32 ether)) {
            revert InsufficientStakedBalance();
        }

        // reduce the eth amount that is verified
        stakedButUnverifiedNativeETH -= (validatorFields.length * (32 ether));

        eigenPod.verifyWithdrawalCredentials(
            beaconTimestamp, stateRootProof, validatorIndices, validatorFieldsProofs, validatorFields
        );
    }
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

**File:** contracts/external/eigenlayer/interfaces/IEigenPod.sol (L56-57)
```text
    /// @dev Thrown if a validator is exiting the beacon chain.
    error ValidatorIsExitingBeaconChain();
```

**File:** contracts/external/eigenlayer/interfaces/IEigenPod.sol (L196-197)
```text
     * @dev Withdrawal credential proofs MUST NOT be older than `currentCheckpointTimestamp`.
     * @dev Validators proven via this method MUST NOT have an exit epoch set already.
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

**File:** contracts/LRTOracle.sol (L244-250)
```text
        if (!protocolPaused && totalETHInProtocol > previousTVL) {
            uint256 rewardAmount = totalETHInProtocol - previousTVL;
            protocolFeeInETH = (rewardAmount * lrtConfig.protocolFeeInBPS()) / 10_000;
        }

        // compute new rsETH price based on total ETH minus fee
        uint256 newRsETHPrice = (totalETHInProtocol - protocolFeeInETH).divWad(rsethSupply);
```

**File:** contracts/LRTOracle.sol (L299-307)
```text
        if (protocolFeeInETH > 0) {
            // Calculate rsETH amount to mint as protocol fee
            uint256 rsethAmountToMintAsProtocolFee = protocolFeeInETH.divWad(newRsETHPrice);

            _checkAndUpdateDailyFeeMintLimit(rsethAmountToMintAsProtocolFee);
            if (rsethAmountToMintAsProtocolFee > 0) {
                address treasury = lrtConfig.getContract(LRTConstants.PROTOCOL_TREASURY);
                IRSETH(rsETHTokenAddress).mint(treasury, rsethAmountToMintAsProtocolFee);
                emit FeeMinted(treasury, rsethAmountToMintAsProtocolFee);
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
