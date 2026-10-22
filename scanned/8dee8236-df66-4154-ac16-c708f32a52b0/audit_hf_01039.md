# [M] Attacker can spam function deposit() to always increase price

## Summary
Severity: Medium
Contest weight: 0.3980
Dataset id: 3971
Source: https://huggingface.co/datasets/Zaevlad/audit-findings-dataset
Type: audit-finding

## Details
In AuctionV1Base, there are multiple rounds with fluctuating prices, depending on user demand. User demand is tracked by the prevRoundDeposits variable, which increases each time a user makes a deposit.
```solidity
function deposit(uint256 amount) public payable {
    if(deposits[_msgSender()] == 0) {
        participants.push(_msgSender());
    }
    deposits[_msgSender()] += amount;
    // @audit Attacker can spam to fake demand and always increase price
    prevRoundDeposits += 1;
}
```
However, the deposit() function can be called to deposit as little as 1 wei, yet the prevRoundDeposits still increases. An attacker could exploit this by repeatedly calling deposit(), creating the illusion of high demand and driving prices up. Even without buying a ticket, they could force others to pay more.

## Recommendation
Consider adjusting the code to only increase prevRoundDeposits when users deposit an amount equal to or greater than the current ticket price.
