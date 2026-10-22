# [H] EtherFiLib::_initiateWithdrawImpl will revert

## Summary
Severity: High
Contest weight: 0.7673
Dataset id: 22987
Source: https://huggingface.co/datasets/Zaevlad/audit-findings-dataset
Type: audit-finding

## Details
EtherFiLib::_initiateWithdrawImpl will revert because rebase tokens transfer 1-2 less wei.
The protocol always assumes that the amount of tokens received is equal to the amount of tokens transferred. This is not the case for rebasing tokens, such as stETH and eETH, because internally they transfer shares which generally results in the received amount of tokens being lower than the requested one by a couple of wei because of roundings: transferring 1e18 eETH tokens from A to B, will may result in B receiving 0.99999e18 eETH tokens.
```solidity
function _initiateWithdrawImpl(uint256 weETHToUnwrap) internal returns (uint256 requestId) {
    uint256 eETHReceived = weETH.unwrap(weETHToUnwrap);
    eETH.approve(address(LiquidityPool), eETHReceived);
    return LiquidityPool.requestWithdraw(address(this), eETHReceived);
}
```
• 1 Unwraps weETHToUnwrap weETH, meaning Transfers eETHReceived of eETH from the weETH contract to this contract itself
• 2 RequestWithdraw eETHReceived, which will attempt to transfer eETHReceived from the contract to the Etherfi protocol But the actual amount of eETH received may be eETHReceived - 1~2 wei.
Step 2 will fail, because the contract doesn't have enough eETH. The issue lies in attempting to transfer eETHReceived of eETH in step 2 instead of wrapping the actual amount of tokens received. Contract functionality DoS.

## Recommendation
```solidity
function _initiateWithdrawImpl(uint256 weETHToUnwrap) internal returns (uint256 requestId) {
    uint256 balanceBefore = eETH.balanceOf(address(this));
    uint256 eETHReceived = weETH.unwrap(weETHToUnwrap);
    uint256 balanceAfter = eETH.balanceOf(address(this));
    eETH.approve(address(LiquidityPool), balanceAfter - balanceBefore);
    return LiquidityPool.requestWithdraw(address(this), balanceAfter - balanceBefore);
}
```
