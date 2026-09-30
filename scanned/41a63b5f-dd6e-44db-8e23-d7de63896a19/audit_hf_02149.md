# [H] Improved Logic in inCaseTokensGetStuck()

## Summary
Severity: High
Contest weight: 0.5844
Dataset id: 12044
Source: https://huggingface.co/datasets/Zaevlad/audit-findings-dataset
Type: audit-finding

## Details
As mentioned in Section 3.4, the FarmHero protocol provides incentive mechanisms that reward the staking of supported assets with certain reward tokens. The rewards are carried out by designating a number of staking pools into which supported assets can be staked. Each pool has its allocPoint*100%/totalAllocPoint share of scheduled rewards and the rewards for stakers are proportional to their share of LP tokens in the pool. Our analysis also reveals a privileged function inCaseTokensGetStuck() that needs to be improved to prevent user pool tokens from being taken. To elaborate, we show below the full implementation of this function. This function is a rather straightforward one in transferring out the requested token. However, it only validates the input token is not the HERO token and fails to ensure the token should not be any staked pool token. Otherwise, the staked funds from participating users may be at risk.
```solidity
function inCaseTokensGetStuck(address _token, uint256 _amount) public onlyOwner {
    require(_token != HERO, "!safe");
    IERC20(_token).safeTransfer(msg.sender, _amount);
}
```

## Recommendation
Correct the above inCaseTokensGetStuck() function by preventing the staked pool tokens from being possibly transferred out.
