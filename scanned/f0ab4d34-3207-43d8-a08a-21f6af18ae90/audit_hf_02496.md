# [M] Staking: rebase

## Summary
Severity: Medium
Contest weight: 0.5676
Dataset id: 13356
Source: https://huggingface.co/datasets/Zaevlad/audit-findings-dataset
Type: audit-finding

## Details
In the staking contract, the rebase function can only be called once per epoch.

In the rebase function, the rewards of the current epoch are used in the next epoch, which can cause the rewards to be updated incorrectly and lead to incorrect distribution of user rewards.

```solidity
function rebase() public {
    // we know about the issues surrounding block.timestamp, using it here will not cause any problems
    if (epoch.endTime <= block.timestamp) {
        IYieldy(YIELDY_TOKEN).rebase(epoch.distribute, epoch.number); // 懒更新

        epoch.endTime = epoch.endTime + epoch.duration;
        epoch.timestamp = block.timestamp;
        epoch.number++;

        uint256 balance = contractBalance();
        uint256 staked = IYieldy(YIELDY_TOKEN).totalSupply();

        if (balance <= staked) {
            epoch.distribute = 0;
        } else {
            epoch.distribute = balance - staked;
        }
    }
}
```

## Recommendation
Put `IYieldy(YIELDY_TOKEN).rebase` after epoch.distribute update

```solidity
function rebase() public {
    // we know about the issues surrounding block.timestamp, using it here will not cause any problems
    if (epoch.endTime <= block.timestamp) {
        uint256 balance = contractBalance();
        uint256 staked = IYieldy(YIELDY_TOKEN).totalSupply();

        if (balance <= staked) {
            epoch.distribute = 0;
        } else {
            epoch.distribute = balance - staked;
        }
        IYieldy(YIELDY_TOKEN).rebase(epoch.distribute, epoch.number);

        epoch.endTime = epoch.endTime + epoch.duration;
        epoch.timestamp = block.timestamp;
        epoch.number++;
    }
}
```

This is how the system is designed.

Changing to Medium. It makes sense that the rebase happens after rewards so that those who enter later don’t affect the distribution of rewards before they joined.
