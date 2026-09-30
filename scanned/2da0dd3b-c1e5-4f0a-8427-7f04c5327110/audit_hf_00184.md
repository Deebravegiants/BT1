# [M] `YAxisVotePower.balanceOf` can be manipulated

## Summary
Severity: Medium
Contest weight: 0.3992
Dataset id: 988
Source: https://huggingface.co/datasets/Zaevlad/audit-findings-dataset
Type: audit-finding

## Details
The `YAxisVotePower.balanceOf` contract uses the Uniswap pool reserves to compute a `_lpStakingYax` reward:
```solidity
(uint256 _yaxReserves,,) = yaxisEthUniswapV2Pair.getReserves();
int256 _lpStakingYax = _yaxReserves
    .mul(_stakeAmount)
    .div(_supply)
    .add(rewardsYaxisEth.earned(_voter));
```
The pool can be temporarily manipulated to increase the `_yaxReserves` amount.

## Recommendation
One could build a TWAP-style contract that tracks a time-weighted-average reserve amount (instead of the price in traditional TWAPs). This can then not be manipulated by flashloans.

I disagree with the “sponsor disputed” tag.

I think this is a valid issue and makes `balanceOf(_voter)` susceptible to flashloan attacks. However, as long as `balanceOf(_voter)` is always called by a trusted EOA during governance vote counts, this should not be a problem. I assume this is the case for governance proposals. If that is not the case, I would recommend changing the code. Otherwise, changing the risk to “documentation” would be reasonable.

Agree with original warden finding, as well as severity

The ability to trigger the count at any time does prevent a flashloan attack (as flashloans are atomic) It would allow the privilege of the flashloan attack to the trusted EOA (admin privilege)

Additionally the voting power can still be frontrun, while you cannot manipulate that voting power via a flashloan, you can just buy and sell your position on the same block as when the count is being taken

Due to this I will up the severity back to medium as this is a legitimate vector to extract value
