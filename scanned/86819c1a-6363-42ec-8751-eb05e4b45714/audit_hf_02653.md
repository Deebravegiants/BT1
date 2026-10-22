# [M] Checks-Effects-Interactions Pattern Violations In NodeDelegator

## Summary
Severity: Medium
Contest weight: 0.4256
Dataset id: 14379
Source: https://huggingface.co/datasets/Zaevlad/audit-findings-dataset
Type: audit-finding

## Details
NodeDelegator implements several functions that violate the Checks-Effects-Interactions (CEI) pattern. Most notably in stake32Eth() on line [163], the EigenLayer contract gets control of the execution flow while the Kelp contracts are in an intermediate state. Speciﬁcally, the rsETH price invariant is broken - 32 ETH has left the Kelp contracts but stakedButUnverifiedNativeETH has not yet been increased. This means that the EigenLayer contracts, or any sub-call, could call updateRSETHPrice() and get an incorrect rsETH price. Deposits and withdrawals could then be made assuming this incorrect price, leading to protocol losses:
```solidity
NodeDelegator.sol
function stake32Eth(
    bytes calldata pubkey,
    bytes calldata signature,
    bytes32 depositDataRoot
)
    external
    whenNotPaused
    onlyLRTOperator
{
    IEigenPodManager eigenPodManager = IEigenPodManager(lrtConfig.getContract(LRTConstants.EIGEN_POD_MANAGER));
    eigenPodManager.stake{ value: 32 ether }(pubkey, signature, depositDataRoot);
    // tracks staked but unverified native ETH
    stakedButUnverifiedNativeETH += 32 ether;
    emit ETHStaked(pubkey, 32 ether);
}
```
Other functions where CEI violations occur: stake32EthValidated() on line [196], verifyWithdrawalCredentials() on line [226], completeUnstaking() on line [345]

## Recommendation
Restructure the functions in question to follow the Checks-Effects-Interactions pattern.
LRT – Smart Contract Updates
