# [M] Fees are paid by the wrong contract

## Summary
Severity: Medium
Contest weight: 0.5526
Dataset id: 10121
Source: https://huggingface.co/datasets/Zaevlad/audit-findings-dataset
Type: audit-finding

## Details
The burn method calls the harvest function which collects the rewards and is intended to pay the fees to the governance contract. This is done by calling the _chargeFee functions inside the FeeBase contract.
```solidity
function _chargeFee(IERC20 token, uint256 earnings) internal {
    token.safeTransfer(rewardFeeDestination, feeToCharge);
    emit RewardFeeCharged(earnings, feeToCharge, rewardFeeDestination);
}
```
The problem is that safeTransfer is used which means that the feeToCharge is send from the FeeBase contract which is not designed to store any tokens. Thus, the transaction will fail. The _chargeFee function is called by the MasterchefAToken contract which is the msg.sender in this case.

## Recommendation
The fees are calculated on the earnings of the MasterchefAToken contract which collects the rewards. Make sure the correct contract is paying the fees.
```solidity
function _chargeFee(IERC20 token, uint256 earnings) internal {
    token.safeTransfer(rewardFeeDestination, feeToCharge);
    token.safeTransferFrom(msg.sender, rewardFeeDestination, feeToCharge);
    emit RewardFeeCharged(earnings, feeToCharge, rewardFeeDestination);
}
```
