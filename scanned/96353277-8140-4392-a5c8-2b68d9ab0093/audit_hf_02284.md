# [M] Revisited Logic to Accumulate Rewards for vlMGP

## Summary
Severity: Medium
Contest weight: 0.4328
Dataset id: 12495
Source: https://huggingface.co/datasets/Zaevlad/audit-findings-dataset
Type: audit-finding

## Details
In the MagpieV2 protocol, the MasterMagpie contract is a customized implementation of MasterChef, which incentivizes user deposits of the supported assets with MGP. In particular, one of the supported assets is vlMGP which is minted to users for their lock of MGP tokens in the VLMGP contract. While examining the MGP rewards calculation for the deposit of vlMGP, we notice the vlMGP in cool down state is not taken into account to share the rewards. To elaborate, we show below the code snippet of the _calLpSupply() routine which is used to calculate the total supply for the given pool. Normally the total supply, i.e., lpSupply, is the amount of the staking token that is locked in the contract (line 676). Specially, for vlMGP, the total supply is retrieved from the VLMGP::totalLocked() routine (line 674). In the VLMGP::totalLocked() routine, it returns the total amount of vlMGP that is not in cool down state (line 109). However, it is designed that the cool-down vlMGP can also receive rewards, and only the fully unlocked vlMGP can not receive rewards.
```solidity
function _calLpSupply(address _stakingToken) internal view returns (uint256) {
    if (_stakingToken == address(vlmgp))
        return IVLMGP(vlmgp).totalLocked();
    return IERC20(_stakingToken).balanceOf(address(this));
}

function totalLocked()
    override
    public
    view
    returns (uint256)
{
    return this.totalSupply() - this.totalAmountInCoolDown();
}
```

## Recommendation
Revisit the _calLpSupply() routine and take the vlMGP that is in cool down state into the total supply to share the rewards.
