# [H] Lack of Timelocked finalWithdraw() in DackiePadInitializableV5/V6

## Summary
Severity: High
Contest weight: 0.5917
Dataset id: 11846
Source: https://huggingface.co/datasets/Zaevlad/audit-findings-dataset
Type: audit-finding

## Details
The DackieSwap protocol features the IDO support with the deployable DackiePadInitializableV5 and DackiePadInitializableV6 contracts. In the process of examining the IDO support, we notice a potential issue of an admin function finalWithdraw() which needs to be better revisited. To elaborate, we show below the implementation of this admin routine finalWithdraw(). While it is protected with the onlyOwner modifier, we notice this routine may be called to withdraw all funds from the IDO contracts. This capability may be concerning to the protocol users. A better approach is to add a timelock so that it may not be able to invoke until the vesting duration is over.
```solidity
function finalWithdraw(uint256 _lpAmount, uint256 _offerAmount) external override onlyOwner {
    require(_lpAmount <= raiseToken.balanceOf(address(this)), "Operations: Not enough tokens");
    require(_offerAmount <= offeringToken.balanceOf(address(this)), "Operations: Not enough offering tokens");
    if (_lpAmount > 0) {
        raiseToken.safeTransfer(msg.sender, _lpAmount);
        if (_offerAmount > 0) {
            offeringToken.safeTransfer(msg.sender, _offerAmount);
        }
    }
    emit AdminWithdraw(_lpAmount, _offerAmount);
}
```

## Recommendation
Revisit the above finalWithdraw() routine so that even the privileged admin may not withdraw the funds from the IDO contract at will.
