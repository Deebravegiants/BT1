# [H] claimTeamTokens function allows infinite claims by the team

## Summary
Severity: High
Contest weight: 0.6143
Dataset id: 8766
Source: https://huggingface.co/datasets/Zaevlad/audit-findings-dataset
Type: audit-finding

## Details
The claimTeamTokens function in the HolofairToken contract is designed to allow the team to claim their allocated tokens after the presale has ended successfully. The function calculates the amount of tokens that can be claimed based on the elapsed time since the end of the fundraising period and the total team allocation. However, the function does not track the amount of tokens that have already been claimed by the team. This oversight allows the team to repeatedly claim the full vested amount, potentially depleting the token supply allocated to users. The function should instead maintain a record of the claimed tokens and subtract this from the vestedAmount to determine the correct amount of tokens the team should receive in each claim.
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
Modify the claimTeamTokens function to include a mechanism for tracking the total amount of tokens claimed by the team. This can be achieved by introducing a new state variable, such as claimedTeamTokens, which is updated each time the team claims tokens. The vestedAmount should then be calculated by subtracting claimedTeamTokens from the total claimable amount. This ensures that the team can only claim the tokens they are entitled to, preventing any potential abuse of the function.
