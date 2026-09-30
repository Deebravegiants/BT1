# [H] Incorrect Accounting for stakedButUnverifiedNativeETH

## Summary
Severity: High
Contest weight: 0.7862
Dataset id: 14378
Source: https://huggingface.co/datasets/Zaevlad/audit-findings-dataset
Type: audit-finding

## Details
stakedButUnverifiedNativeETH does not take into account an effective balance of the validator at the time of calculation, which may result in inaccurate accounting.
stakedButUnverifiedNativeETH in NodeDelegator describes the amount of ETH that is staked on EigenLayer, but that has not yet been verified and, as such, will not be reflected in eigenPodManager.podOwnerShares(). This is used to ensure that accounting is correct during this time and all of the protocol’s assets are accounted for. To do this, stakedButUnverifiedNativeETH is incremented by 32 ETH when stake32ETH() is called, and is decremented again after verification.
```solidity
NodeDelegator.sol
IEigenPodManager eigenPodManager = IEigenPodManager(lrtConfig.getContract(LRTConstants.EIGEN_POD_MANAGER));
eigenPodManager.stake{ value: 32 ether }(pubkey, signature, depositDataRoot);
// tracks staked but unverified native ETH
stakedButUnverifiedNativeETH += 32 ether;
```
However, stakedButUnverifiedNativeETH is subtracted by the effective balance of the validator, not 32 ETH. This presents an edge case where a validator may have an effective balance lower than 32 ETH during veriﬁcation. This would result in stakedButUnverifiedNativeETH containing some left-over ETH, which is counted towards the protocols funds, but is not actually owned by the protocol, resulting in inaccurate accounting and an incorrect rsETH price.
```solidity
NodeDelegator.sol
eigenPod.verifyWithdrawalCredentials(
oracleTimestamp, stateRootProof, validatorIndices, withdrawalCredentialProofs, validatorFields
);
uint256 totalVerifiedEthGwei = 0;
for (uint256 i = 0; i < validatorFields.length;) {
    // TODO: Handle case when effective balance goes below 32 eth
    // in case of validator with extra stakes, this will count 32 eth as that is max effective balance
    uint64 validatorCurrentBalanceGwei = BeaconChainProofs.getEffectiveBalanceGwei(validatorFields[i]);
    totalVerifiedEthGwei += validatorCurrentBalanceGwei;
    unchecked {
        // reduce the eth amount that is verified
        stakedButUnverifiedNativeETH -= (totalVerifiedEthGwei * LRTConstants.ONE_E_9);
    }
}
```
LRT – Smart Contract Updates

## Recommendation
Modify the accounting calculation of stakedButUnverifiedNativeETH to ensure it represents correct balances at all times.
