# [M] Users can exploit the system by depositing 1 wei

## Summary
Severity: Medium
Contest weight: 0.4093
Dataset id: 3995
Source: https://huggingface.co/datasets/Zaevlad/audit-findings-dataset
Type: audit-finding

## Details
In the LotteryV2Base contract, buyers can roll a dice to generate a random number. Those who roll numbers close to the seller's number become eligible for minting.
Each roll requires a rollPrice. However, users receive a "free" roll in the deposit() function. This can be exploited by an attacker. The attacker might only deposit 1 wei into the contract to get this "free" roll, and then deposit the necessary amount to claim the number if they roll a winning number. If they don't roll a winning number, they can withdraw.
```solidity
function deposit(uint256 amount) public lotteryStarted hasNotWonInLotteryV1(_msgSender()) {
    require(amount > 0, "No funds sent");
    require(
        amount,
        "Insufficient allowance"
    );
    if (deposits[_msgSender()] == 0) {
        participants.push(_msgSender());
    }
    deposits[_msgSender()] += amount;
    // @audit Free roll
    if (rolledNumbers[_msgSender()] == 0) {
        _requestRandomness(abi.encode(_msgSender()));
        emit RandomRequested(_msgSender());
    }
}
```

## Recommendation
Consider charging the rollPrice in the deposit() function.
