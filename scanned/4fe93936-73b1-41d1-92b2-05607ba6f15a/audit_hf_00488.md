# [H] Lender group members can be

## Summary
Severity: High
Contest weight: 0.7851
Dataset id: 1930
Source: https://huggingface.co/datasets/Zaevlad/audit-findings-dataset
Type: audit-finding

## Details
Adversaries can constantly reset the withdrawal delay of lender group members by performing 0-value transferFrom transactions to invoke the afterTokenTransfer hook.
Description
Currently there is a delay on withdrawals to prevent sandwich attacks in lender group contracts. Members must invoke prepareSharesForBurn by stating how many shares they want to burn and start an internal countdown. Afterwards, members invoke burnSharesTo WithdrawEarnings which checks whether the delay passed in burn
```solidity
function burn(address _burner, uint256 _amount, uint256 withdrawDelayTimeSeconds) external onlyOwner {
    //require prepared
    require(poolSharesPreparedToWithdrawForLender[_burner] >= _amount,"Shares not prepared for withdraw");
    require(poolSharesPreparedTimestamp[_burner] <= block.timestamp - withdrawDelayTimeSeconds,"Shares not prepared for withdraw");
    //reset prepared
    poolSharesPreparedToWithdrawForLender[_burner] = 0;
    poolSharesPreparedTimestamp[_burner] = block.timestamp;
    _burn(_burner, _amount);
}
```
This countdown is reset every time a member invokes a share transfer through the _after TokenTransfer hook presumably to prevent users preparing shares in advance by transferring it between one another.
```solidity
function _afterTokenTransfer(
    address from,
    address to,
    uint256 amount
) internal override {
    //reset prepared
    poolSharesPreparedToWithdrawForLender[from] = 0;
    poolSharesPreparedTimestamp[from] = block.timestamp;
}
```
Adversaries can perform 0-value transferFrom transactions which will always pass as there are no 0-value checks in OZ's version 4.8 ERC20.sol used by the protocol. Users will have their countdown constantly reset thus being prevented from withdrawing forever or until a bribe is paid.
• OpenZeppelin's ERC20.transferFrom has no 0-value input validation
• LenderCommitmentGroupShares._afterTokenTransfer does not perform 0-value input either.
Internal pre-conditions
Group members must have invoked prepareSharesForBurn
External pre-conditions
None
Attack Path
1. Group member invokes prepareSharesForBurn starting the countdown
2. Adversary invokes transferFrom(victim,to,0) minutes before the cooldown expires
3. Cooldown and shares are reset because _afterTokenTransfer was triggered
4. Group member is forced to re-prepare their shares
5. Attacker repeats this continuously or until a bribe is paid
Lender commit group members will have their funds permanently locked in the contract

## Recommendation
Rewrite the hook to be skipped in case of amount=0
