# [M] Weights are not updated on each _update action but only when nearing the target time, due to precision loss

## Summary
Severity: Medium
Chain: Smart contract
Component: Catalyst-Exchange
Published: 2024-02-03
Source: https://github.com/hats-finance/Catalyst-Exchange-0x3026c1ea29bf1280f99b41934b2cb65d053c9db4/issues/78
Type: hats-finding

## Details
**Github username:** @nuthan2x
**Twitter username:** nuthan2x
**Submission hash (on-chain):** 0x75401aa9cc642d6ae1209ca04b56d7e3b72e29d10e255d616f92bcccd2d19f77
**Severity:** medium

**Description:**
**Description**\
The weights of the vaults can be updated by vault deployer due to market conditions and adaptability. And the weights are updated on each transaction of swap/liquidity actions, and they will be linearly updated until the target time is reached. But some weights changes are not updated during the first 85% of the time but only starts to update on the rest 15%. This is due to the presion loss mentioned in the below sections.

**Attack Scenario**\
- Code from [CatalystVaultVolatile::_updateWeights](https://github.com/hats-finance/Catalyst-Exchange-0x3026c1ea29bf1280f99b41934b2cb65d053c9db4/blob/27b4d0a2bca177aff00def8cd745623bfbf7cb6b/evm/src/CatalystVaultVolatile.sol#L240-L242)

```solidity
    if (targetWeight > currentWeight) {
        // if the weights are increased then targetWeight - currentWeight > 0.
        // Add the change to the current weight.
        uint256 newWeight = currentWeight + (
@--->        (targetWeight - currentWeight) * (block.timestamp - lastModification)
@--->   ) / (adjTarget - lastModification);
        _weight[token] = newWeight;
        wsum += newWeight;
    } else {
        // if the weights are decreased then targetWeight - currentWeight < 0.
        // Subtract the change from the current weights.
        uint256 newWeight = currentWeight - (
            (currentWeight - targetWeight) * (block.timestamp - lastModification)
        ) / (adjTarget - lastModification);
        _weight[token] = newWeight;
        wsum += newWeight;
    }
```

- The issue is due to the huge denominator in the above code at `(adjTarget - lastModification)` ex: (14 days - 1 hours), but numerator will be `(targetWeight - currentWeight) * (block.timestamp - lastModification)` ex: (20 - 10) * (1 hours) which is a precision loss.

Exact flow of issue:

1. create a vault with (50% per each asset weight) at [10,10] being the weights.
2. Now due to market conditions, the vault deployer changes the weights to (66% - 33%) in [20,10] as the weights for 14 days adjustment period.

_Trimmed to 38 lines — full report: https://github.com/hats-finance/Catalyst-Exchange-0x3026c1ea29bf1280f99b41934b2cb65d053c9db4/issues/78_
