# [M] Predefined amount parameter can challenge

## Summary
Severity: Medium
Contest weight: 0.4524
Dataset id: 22959
Source: https://huggingface.co/datasets/Zaevlad/audit-findings-dataset
Type: audit-finding

## Details
Deposits need not be allocated to Obol validators In StakingModule, the amount to be deposited in Lido is supposed to go to the Obol validators. But the only check kept for this is that the stakingModuleId is set to SimpleDVT module id in Lido and unfinalizedstETH <= bufferedETH link
```solidity
function convertAndDeposit(
    uint256 amount,
    uint256 blockNumber,
    bytes32 blockHash,
    bytes32 depositRoot,
    uint256 nonce,
    bytes calldata depositCalldata,
    IDepositSecurityModule.Signature[] calldata sortedGuardianSignatures
) external onlyDelegateCall {
    if (IERC20(weth).balanceOf(address(this)) < amount)
    uint256 unfinalizedStETH = withdrawalQueue.unfinalizedStETH();
    uint256 bufferedEther = ISteth(steth).getBufferedEther();
    if (bufferedEther < unfinalizedStETH)
        revert InvalidWithdrawalQueueState();
    _wethToWSteth(amount);
    depositSecurityModule.depositBufferedEther(
        blockNumber,
        blockHash,
        depositRoot,
        stakingModuleId,
        nonce,
        depositCalldata,
        sortedGuardianSignatures
    );
}
```
There is no enforcement/checks kept on the amount param. It is possible to pass in any value for the amount param or the buffered ETH amount in lido to change from the value using which the amount was calculated before the call due to other deposits. This allows for scenarios where the amount is not deposited into validators at all (not in multiples of 32 eth), could be shared with other staking modules or could result in reverts due to the max limit restriction in the lido side. There is also no enforcement that the deposits made would be allocated to Obol validators itself since the simpleDVT staking module in Lido also contains SSV operators The amount to be staked for obol validators can be assigned to other operators

## Recommendation
Add checks for the operators and calculate the maximum amount depositable to that set at the instant of the call rather than a predefined value
