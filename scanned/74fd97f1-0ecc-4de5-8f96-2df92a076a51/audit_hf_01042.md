# [M] Unbounded loop can prevent seller from withdrawing funds

## Summary
Severity: Medium
Contest weight: 0.6628
Dataset id: 3974
Source: https://huggingface.co/datasets/Zaevlad/audit-findings-dataset
Type: audit-finding

## Details
In LotteryV2, the winner is picked from how close their random number is to the sellers random number.
When a buyer has won, their win is automatically claimed from the VRF call to fulfillRandomness:
```solidity
} else {
    rolledNumbers[requestedBy] = _randomNumber;
    claimNumber(requestedBy);
}
```
And in claimNumber:
```solidity
if (isClaimable(_participant)) {
    winners[_participant] = true;
    winnerAddresses.push(_participant);
    emit WinnerSelected(_participant);
    return true;
} else {
    return false;
}
```
winnerAddresses is then iterated over and each winners deposit is added up and sent (after taking protocol tax) to the seller in sellerWithdraw.
The issue is that claimNumber can be called by anyone any number of times. Each call the winner is added to winnerAddresses again. This could be used repeatedly to make the list so large that the gas for the transaction would not fit in a block.

## Recommendation
Consider checking if a user has already claimed before adding to winnerAddresses:
```solidity
- if (isClaimable(_participant)) {
+ if (isClaimable(_participant) && !winners[_participant]) {
```
