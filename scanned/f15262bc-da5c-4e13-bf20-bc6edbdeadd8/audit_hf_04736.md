# [M] TOFTMarketReceiverModule::marketBorrowReceiver

## Summary
Severity: Medium
Contest weight: 0.5928
Dataset id: 22559
Source: https://huggingface.co/datasets/Zaevlad/audit-findings-dataset
Type: audit-finding

## Details
The TOFTMarketReceiverModule::marketBorrowReceiver flow is broken and will revert when the Magnetar contract tries to transfer the ERC1155 tokens to the Market contract. TOFTMarketReceiverModule::marketBorrowReceiver flow is broken. Let's examine it more closely:
• After checking the whitelisting status for the marketHelper, magnetar and the market contracts an approval is made to the Magnetar contract.
• MagnetarCollateralModule::depositAddCollateralAndBorrowFromMarket get called with the passed parameters.
• If the data.deposit is true, the Magnetar contract will call _extractTokens with the following params: from = msg_.user, token = collateralAddress and amount = msg_.collateralAmount.
```solidity
function _extractTokens(address _from, address _token, uint256 _amount) internal returns (uint256) {
    uint256 balanceBefore = IERC20(_token).balanceOf(address(this));
    // IERC20(_token).safeTransferFrom(_from, address(this), _amount);
    pearlmit.transferFromERC20(_from, address(this), address(_token), _amount);
    uint256 balanceAfter = IERC20(_token).balanceOf(address(this));
    if (balanceAfter <= balanceBefore) revert Magnetar_ExtractTokenFail();
    return balanceAfter - balanceBefore;
}
```
• The collateral gets transferred into the Magnetar contract in case the msg._user has given sufficient allowance to the Magnetar contract through the Pearlmit contract.
• After this _setApprovalForYieldBox(data.market, yieldBox_); is called that sets the allowance of the Magnetar contract to the Market contract.
• Then addCollateral is called on the Market contract. I've inlined the internal function to make it easier to follow:
```solidity
function _addCollateral(address from, address to, bool skim, uint256 amount, uint256 share) internal {
    if (share == 0) {
        share = yieldBox.toShare(collateralId, amount, false);
    }
    uint256 oldTotalCollateralShare = totalCollateralShare;
    userCollateralShare[to] += share;
    totalCollateralShare = oldTotalCollateralShare + share;
    // yieldBox.transfer(from, address(this), _assetId, share);
    bool isErr = pearlmit.transferFromERC1155(from, address(this), address(yieldBox), collateralId, share);
    if (isErr) {
        revert TransferFailed();
    }
}
```
• After the userCollateralShare mapping is updated pearlmit.transferFromERC1155(from, address(this), address(yieldBox), collateralId, share); gets called.
• This is critical as now the Magnetar is supposed to transfer the ERC1155 tokens (Yieldbox) to the Market contract.
• In order to do this the Magnetar contract should have given the allowance to the Market contract through the Pearlmit contract.
• This is not the case, the Magnetar has only executed _setApprovalForYieldBox(data.market, yieldBox_);, nothing else.
• It will revert inside the Pearlmit contract transferFromERC1155 function when the allowance is being checked.
Other occurrences
1. TOFT::mintLendXChainSGLXChainLockAndParticipateReceiver has a similar issue as:
• Extract the bbCollateral from the user, sets approval for the BigBang contract through YieldBox.
• But then inside the BBCollateral::addCollateral the _addTokens again expects an allowance through the Pearlmit contract.
2. TOFT::lockAndParticipateReceiver calls the Magnetar:lockAndParticipate where:
```solidity

## Recommendation
Review all the allowance mechanisms and ensure that they are correct.
