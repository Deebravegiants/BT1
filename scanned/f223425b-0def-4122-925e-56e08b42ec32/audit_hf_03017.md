# [M] StakingRewards: recoverERC20

## Summary
Severity: Medium
Contest weight: 0.5620
Dataset id: 16884
Source: https://huggingface.co/datasets/Zaevlad/audit-findings-dataset
Type: audit-finding

## Details
Similar to <https://github.com/code-423n4/2022-02-concur-findings/issues/210> StakingRewards.recoverERC20 rightfully checks against the stakingToken being sweeped away. However, there’s no check against the rewardsToken. This is the case of an admin privilege, which allows the owner to sweep the rewards tokens, perhaps as a way to rug depositors.

```solidity
function recoverERC20(address tokenAddress, uint256 tokenAmount)
    external
    onlyOwner
{
    require(
        tokenAddress != address(stakingToken),
        "Cannot withdraw the staking token"
    );
    ERC20(tokenAddress).safeTransfer(owner, tokenAmount);
    emit Recovered(tokenAddress, tokenAmount);
}
```

## Recommendation
Add an additional check

```solidity
require(
    tokenAddress != address(rewardsToken),
    "Cannot withdraw the rewards token"
);
```

I’m curious what others think about this issue, if users do not receive any reward tokens is that really a problem? Users are still able to withdraw their ERC1155 tokens at any time, and vaults still work as expected. If the admin is malicious, users will miss out on tokens which will be worthless after a rugpull anyway.

This is how synthetix rewards work, I forked their smart contracts.

Including this issue, issues [#50](https://github.com/code-423n4/2022-09-y2k-finance-findings/issues/50), [#51](https://github.com/code-423n4/2022-09-y2k-finance-findings/issues/51) and [#52](https://github.com/code-423n4/2022-09-y2k-finance-findings/issues/52) can be considered to be admin privilege findings. There’s active discussion revolving how findings of this category should be handled / standardized.

For now, I’m keeping the medium severity due to historical context (past contest references). l also reproduce the classification rationale that I gave for a previous contest below:

### Classification and thought process

The issues raised about rugpull vulnerabilities via centralisation risks can be broadly classified into 2 categories:

1. Those that can be mitigated with contract modifications. Examples include:
2. ensuring upper / lower proper bounds on key variables (fees not exceeding max threshold, for instance)
3. adding safeguards and conditional checks (require statements)
4. Those that can’t be strictly enforced
5. Use multisig, put admin under timelock


Category 1 can be separated into the various attack vectors and actors (admin / strategist), as the mitigation is more tangible in nature. This way, the recommended fixes can also be easily identified and adopted. A warden that grouped multiple attack vectors together will have their issue made the primary issue; the rest will be marked as duplicates of it.

Regarding category 2, for issues that are generic “put admin under timelock” without explaining how and why a compromised owner / strategist can rug, as per the rulebook and judges’ general consensus, I will downgrade their severity to QA. Those that explained the impact and vulnerability in detail will be grouped together with medium severity because there isn’t much that can be done about it.
