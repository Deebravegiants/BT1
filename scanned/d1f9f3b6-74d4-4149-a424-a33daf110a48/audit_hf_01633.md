# [H] Incorrect vesting duration used in claimTeamTokens function

## Summary
Severity: High
Contest weight: 0.6136
Dataset id: 8765
Source: https://huggingface.co/datasets/Zaevlad/audit-findings-dataset
Type: audit-finding

## Details
The claimTeamTokens function is designed to allow the team to claim their allocated tokens after the presale has ended successfully. The function calculates the amount of tokens that can be claimed based on the elapsed time since the end of the fundraising period and the total team allocation. However, there is an issue in the calculation of the vestedAmount. The function incorrectly caps the timeElapsed variable using presaleVestingDuration instead of teamVestingDuration. This discrepancy can lead to two potential problems: if presaleVestingDuration is greater than teamVestingDuration, the team may withdraw more tokens than intended, potentially taking tokens that belong to users. Conversely, if presaleVestingDuration is less than teamVestingDuration, some of the tokens allocated to the team may remain locked in the contract indefinitely. The relevant code snippet is as follows:
```solidity
function claimTeamTokens() external nonReentrant {
    require(msg.sender == teamWallet, "Only team can claim team tokens");
    require(!presaleActive, "Presale ongoing");
    require(presaleSuccess, "Presale not successful");
    uint256 totalClaimable = teamAllocation;
    uint256 timeElapsed = block.timestamp - fundraisingEndTime;
    if (timeElapsed > presaleVestingDuration) {
        timeElapsed = presaleVestingDuration;
    }
    uint256 vestedAmount = (totalClaimable * timeElapsed) / teamVestingDuration;
    require(vestedAmount > 0, "No vested tokens available");
    _transfer(address(this), teamWallet, vestedAmount);
    emit TokensWithdrawn(teamWallet, vestedAmount);
}
```

## Recommendation
To resolve this issue, replace presaleVestingDuration with teamVestingDuration when capping the timeElapsed variable.
