# [H] User deposit balance incorrectly zeroed after partial token claim

## Summary
Severity: High
Contest weight: 0.6068
Dataset id: 8767
Source: https://huggingface.co/datasets/Zaevlad/audit-findings-dataset
Type: audit-finding

## Details
The claimTokens function is designed to allow users to claim their vested tokens after a successful presale. The function calculates the amount of tokens a user is entitled to based on their deposit and the elapsed time since the end of the fundraising period. However, there is a critical issue in the implementation: the user's deposit balance is set to zero after a claim, even if the claim is only partial. This means that users lose their remaining deposit balance and are unable to claim any further tokens they are entitled to as they vest over time.
```solidity
function claimTokens() external nonReentrant {
    require(!presaleActive, "Presale ongoing");
    require(presaleSuccess, "Presale not successful");
    uint256 userDeposit = deposits[msg.sender];
    require(userDeposit > 0, "No tokens to claim");
    uint256 totalClaimable = (userDeposit * presaleAllocation) / totalRaised;
    uint256 timeElapsed = block.timestamp - fundraisingEndTime;
    if (timeElapsed > presaleVestingDuration) {
        timeElapsed = presaleVestingDuration;
    }
    uint256 vestedAmount = (totalClaimable * timeElapsed) / presaleVestingDuration;
    require(vestedAmount > 0, "No vested tokens available");
    deposits[msg.sender] = 0;
    _transfer(address(this), msg.sender, vestedAmount);
    emit TokensWithdrawn(msg.sender, vestedAmount);
}
```

## Recommendation
Modify the claimTokens function to track the amount of tokens already withdrawn by the user. Instead of zeroing out the user's deposit balance, maintain a record of the total tokens claimed so far. Subtract this amount from the vestedAmount to determine the number of tokens the user should receive in the current claim. This ensures that users can continue to claim their vested tokens over time without losing their remaining balance.
