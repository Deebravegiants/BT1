# [M] `Auction.sol#settleAuction`

## Summary
Severity: Medium
Contest weight: 0.5492
Dataset id: 908
Source: https://huggingface.co/datasets/Zaevlad/audit-findings-dataset
Type: audit-finding

## Details
```solidity
function withdrawBounty(uint256[] memory bountyIds) internal {
    // withdraw bounties
    for (uint256 i = 0; i < bountyIds.length; i++) {
        Bounty memory bounty = _bounties[bountyIds[i]];
        require(bounty.active);

        IERC20(bounty.token).transfer(msg.sender, bounty.amount);
        bounty.active = false;

        emit BountyClaimed(msg.sender, bounty.token, bounty.amount, bountyIds[i]);
    }
}
```

In the `withdrawBounty` function, `bounty.active` should be set to `false` when the bounty is claimed.

However, since `bounty` is stored in memory, the state update will not succeed.

## Recommendation
Change to:

```solidity
Bounty storage bounty = _bounties[bountyIds[i]];
```

[frank-beard (Kuiper) confirmed and marked as duplicate](https://github.com/code-423n4/2021-09-defiprotocol-findings/issues/136#issuecomment-936623596):**

duplicate of <https://github.com/code-423n4/2021-09-defiprotocol-findings/issues/168>

Finding is valid, because the warden didn’t provide a POC of how to steal user funds, the finding is of medium severity
