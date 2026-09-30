# [M] `StakingRewards.sol` `recoverERC20

## Summary
Severity: Medium
Contest weight: 0.1113
Dataset id: 1567
Source: https://huggingface.co/datasets/Zaevlad/audit-findings-dataset
Type: audit-finding

## Details
[StakingRewards.sol#L166-L176](https://github.com/code-423n4/2022-02-concur/blob/72b5216bfeaa7c52983060ebfc56e72e0aa8e3b0/contracts/StakingRewards.sol#L166-L176)  

    function recoverERC20(address tokenAddress, uint256 tokenAmount)
        external
        onlyOwner
    {
        require(
            tokenAddress != address(stakingToken),
            "Cannot withdraw the staking token"
        );
        IERC20(tokenAddress).safeTransfer(owner(), tokenAmount);
        emit Recovered(tokenAddress, tokenAmount);
    }

## Recommendation
Change to:
    
    function recoverERC20(
        address tokenAddress,
        address to,
        uint256 amount
    ) external onlyOwner {
        require(tokenAddress != address(stakingToken) && tokenAddress != address(rewardsToken), "20");

        IERC20(tokenAddress).safeTransfer(to, amount);
        emit Recovered(tokenAddress, to, amount);
    }

Agree with the finding, ultimately a simple check would provide stronger security guarantees.

Because this is contingent on a malicious owner, I believe Medium Severity to be more appropriate.
