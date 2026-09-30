# [M] Mismatched IncentiveController Invocation in OpenSkyOToken

## Summary
Severity: Medium
Contest weight: 0.5929
Dataset id: 12634
Source: https://huggingface.co/datasets/Zaevlad/audit-findings-dataset
Type: audit-finding

## Details
The OpenSky protocol has the built-in, extensible incentive mechanism with the introduction of _incentivesController that is designed to keep the accounting logic of rewards for protocol users. In the following, we examine the specific interactions with _incentivesController and notice the inconsistent uses during the interactions.
```solidity
interface IOpenSkyIncentivesController {
    function handleAction(
        address account,
        uint256 userBalance,
        uint256 totalSupply
    ) external;
}
```
To elaborate, we show above the handleAction() callback function that is invoked when an user interacts with the protocol. We notice that this function takes three arguments: the first one indicates the related account (line 7), the second one (line 8) shows the current balance at the specific moment when the user interacts with the protocol; and the last one (line 9) is the current total supply of related tokens.
In the following, we show one specific case when the above handleAction() function is invoked. Specifically, it happens when the supported OpenSkyOToken tokens are being transferred. The internal _transfer() routine properly takes a record of current balance of the user as well as the total supply, and then calls the above handleAction() function.
```solidity
function _transfer(
    address sender,
    address recipient,
    uint256 amount
) internal override {
    uint256 index = IOpenSkyPool(_pool).getReserveNormalizedIncome(_reserveId);
    uint256 amountScaled = amount.rayDivTruncate(index);
    require(amountScaled != 0, Errors.AMOUNT_SCALED_IS_ZERO);
    require(amountScaled <= type(uint128).max, Errors.AMOUNT_TRANSFER_OWERFLOW);
    uint256 previousSenderBalance = super.balanceOf(sender);
    uint256 previousRecipientBalance = super.balanceOf(recipient);
    super._transfer(sender, recipient, amountScaled);
    if (address(_incentivesController) != address(0)) {
        uint256 currentTotalSupply = super.totalSupply();
        _incentivesController.handleAction(sender, currentTotalSupply, previousSenderBalance);
        if (sender != recipient) {
            _incentivesController.handleAction(recipient, currentTotalSupply, previousRecipientBalance);
        }
    }
}
```
It comes to our attention that the caller invokes handleAction() with an inconsistent list of arguments. Particularly, the second argument is currentTotalSupply, instead of the expected user balance. Also, the third argument is the user balance (oldSenderBalance/oldRecipientBalance), instead of the expected total supply. A correct function definition of handleAction() needs to switch the order of its current last two arguments.

## Recommendation
Properly revise the _handleAction() invocation with a correct argument order.
