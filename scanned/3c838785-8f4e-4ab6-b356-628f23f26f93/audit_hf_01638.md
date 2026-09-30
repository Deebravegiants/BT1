# [M] withdrawDeposit function allows indefinite locking of user funds

## Summary
Severity: Medium
Contest weight: 0.4088
Dataset id: 8770
Source: https://huggingface.co/datasets/Zaevlad/audit-findings-dataset
Type: audit-finding

## Details
The withdrawDeposit function in the HolofairToken contract is designed to allow users to withdraw their deposited funds during the presale. However, the current implementation restricts withdrawals to only when the presale is active. This means that if the presale is paused, users are unable to withdraw their funds. Since the presale can be paused indefinitely, this creates a risk where users' deposited funds could be locked forever.
```solidity
function withdrawDeposit(uint256 amount) external nonReentrant {
    require(presaleActive, "Presale not active");
    uint256 userDeposit = deposits[msg.sender];
    require(userDeposit >= amount, "Insufficient deposit");
    // Reset the user's deposit before transferring to prevent reentrancy
    deposits[msg.sender] -= amount;
    totalRaised -= amount;
    (bool success, ) = msg.sender.call{value: amount}("");
    require(success, "Withdrawal failed");
    emit WithdrawDeposit(msg.sender, 0, amount);
}
```

## Recommendation
Modify the withdrawDeposit function to allow users to withdraw their funds even when the presale is paused. This can be achieved by removing the require(presaleActive, "Presale not active"); line from the function.
