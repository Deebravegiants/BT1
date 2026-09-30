# [H] twTAP.claimAndSendRewards

## Summary
Severity: High
Contest weight: 0.2945
Dataset id: 19110
Source: https://huggingface.co/datasets/Zaevlad/audit-findings-dataset
Type: audit-finding

## Details
Detailed description of the impact of this finding. twTAP.claimAndSendRewards() will claim the wrong amount for each reward token due to the use of wrong index. As a result, some users will lose some rewards and others will claim more rewards then they deserve.

## Proof of Concept
Provide direct links to all referenced code in GitHub. Add screenshots, logs, or any other relevant proof that illustrates the concept.

twTAP.claimAndSendRewards() allows the tapOFT to claim and send a list of rewards indicated in `_rewardTokens`.

It calls the function `_claimRewardsOn()` to achieve this:

Unfortunately, at L509, it uses the index of `i` instead of the correct index of `claimableIndex`. As a result, the amount that is claimed and transferred for each reward is wrong.

## Recommendation
We need to use index `claimableIndex` instead of `i` for function `_claimRewardsOn()`:

    function _claimRewardsOn(
            uint256 _tokenId,
            address _to,
            IERC20[] memory _rewardTokens
        ) internal {
            uint256[] memory amounts = claimable(_tokenId);
            unchecked {
                uint256 len = _rewardTokens.length;
                for (uint256 i = 0; i < len; ) {
                    uint256 claimableIndex = rewardTokenIndex[_rewardTokens[i]];
    -                uint256 amount = amounts[i];
    +                uint256 amount = amounts[claimableIndex];

                    if (amount > 0) {
                        // Math is safe: `amount` calculated safely in `claimable()`
                        claimed[_tokenId][claimableIndex] += amount;
                        rewardTokens[claimableIndex].safeTransfer(_to, amount);
                    }
                    ++i;
                }
            }
        }
