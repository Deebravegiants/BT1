# [M] Inconsistent Rate Scale Of ControlledRewardPool

## Summary
Severity: Medium
Contest weight: 0.4226
Dataset id: 11680
Source: https://huggingface.co/datasets/Zaevlad/audit-findings-dataset
Type: audit-finding

## Details
The Augmented Finance protocol is a DeFi lending protocol that is inspired from Aave with a variety of improvements and new features. During our analysis, we notice the current reward pools have the advanced mechanism to allow for flexible setting of reward rates. To elaborate, we show below the _setRate() function. As the name indicates, it supports a new reward rate to be assigned. It comes to our attention that when the reward pool is paused, the internal storage state _pausedRate (line 88) is used to save the current reward rate, which is not scaled up to avoid possible precision loss. However, when it is later resumed, the effective reward rate is enforced via internalSetRate(_pausedRate) (line 138), which assumes the rate is already scaled up (similar to line 91). Note the constructor function assumes the initialRate is already scaled up with the multiplication of _rateScale.
```solidity
function _setRate(uint256 rate) private {
    if (isPaused()) {
        _pausedRate = rate;
        return;
    }
    internalSetRate(rate.rayMul(_rateScale));
}

function internalPause(bool paused) internal virtual {
    if (paused) {
        _pausedRate = internalGetRate();
        internalSetRate(0);
        return;
    }
    internalSetRate(_pausedRate);
}
```

## Recommendation
Be consistent in the internal pausedRate state to always have the same _rateScale.
