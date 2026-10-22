# [H] Pending allowances can be exploited

## Summary
Severity: High
Contest weight: 0.6374
Dataset id: 22525
Source: https://huggingface.co/datasets/Zaevlad/audit-findings-dataset
Type: audit-finding

## Details
Pending allowances can be exploited in multiple places in the codebase. TOFT::marketRemoveCollateralReceiver has the following flow:
• It calls removeCollateral ona a market with the following parameters: from = msg_user, to = msg_.removeParams.magnetar.
• Inside the SGLCollateral::removeCollateral _allowedBorrow is called and check if the from = msg_user address has given enough allowanceBorrow to the msg.sender which in this case is the TOFT contract.
• So for a user to use this flow in needs to call:
```solidity
function approveBorrow(address spender, uint256 amount) external returns (bool) {
    _approveBorrow(msg.sender, spender, amount);
    return true;
}
```
• And give the needed allowance to the TOFT contract.
• This results in collateral being removed and transferred into the Magnetar contract with yieldBox.transfer(address(this), to, collateralId, share);.
• The Magnetar gets the collateral, and it can withdraw it to any address specified in the msg_.withdrawParams.
This is problematic as the TOFT::marketRemoveCollateralReceiver doesn't check the msg.sender. In practice this means if Alice has called approveBorrow and gives the needed allowance with the intention of using the marketRemoveCollateralReceiver flow, Bob can use the marketRemoveCollateralReceiver flow and withdraw all the collateral from Alice to his address. So, any pending allowances from any user can immediately be exploited to steal the collateral.

Other occurrences There are a few other occurrences of this problematic pattern in the codebase. TOFT::marketBorrowReceiver expects the user to give an approval to the Magnetar contract. The approval is expected inside the _extractTokens function where pearlmit.transferFromERC20(_from, address(this), address(_token), _amount); is called. Again, the msg.sender is not checked inside the marketBorrowReceiver function, so this flow can be abused by another user to borrow and withdraw the borrowed amount to his address. TOFT::mintLendXChainSGLXChainLockAndParticipateReceiver also allows to borrow inside the BigBang market and withdraw the borrowed amount to an arbitrary address. TOF::exerciseOptionsReceiver has the _internalTransferWithAllowance function that simply allows to transfer TOFT tokens from any _options.from address that has given an allowance to srcChainSender, by anyone that calls this function. It allows to forcefully call the exerciseOptionsReceiver on behalf of any other user. USDO::depositLendAndSendForLockingReceiver also expects the user to give an allowance to the Magnetar contract, i.e. MagnetarAssetXChainModule::depositYBLendSGLLockXchainTOLP calls the _extractTokens. The impact of this vulnerability is that any pending allowances from any user can immediately be exploited to steal the collateral/borrowed amount.

## Recommendation
There are multiple instances of issues with dangling allowances in the protocol. Review all the allowance flows and make sure it can't be exploited.
