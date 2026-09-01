# [M] Stakers in the NativeVault could be unfairly slashed.

## Summary
Severity: Medium
Chain: Smart contract
Component: 2024-09-karak-mitigation
Published: 2024-09-15
Source: https://github.com/code-423n4/2024-09-karak-mitigation-findings/issues/16
Type: code-finding

## Details
# Lines of code

https://github.com/karak-network/karak-arena-mitigations/blob/475cfd73744cabe239720feec4a227a739910119/src/NativeVault.sol#L509-L517


# Vulnerability details

## Bug description
> Note: Even though the root cause of the issue was not discovered in the previous audit, the presented scenario is the same as in [M-02](https://github.com/code-423n4/2024-07-karak-findings/issues/31).

Consider a scenario where both Alice and Bob each have 32 ETH restaked into the NativeVault. NativeVault's `totalAssets` equals 64 ETH. A slashing event occurs in the vault, resulting in the NativeVault being slashed by 2 ETH, reducing `totalAssets` to 62 ETH.

[NativeVault.sol#L312](https://github.com/karak-network/karak-arena-mitigations/blob/475cfd73744cabe239720feec4a227a739910119/src/NativeVault.sol#L312)
```solidity
self.totalAssets -= totalAssetsToSlash;
```

Now 32 shares of both users amount to `32 * 62 / 64 = 31 ETH`, meaning that both Alice and Bob lost 1 ETH due to the slashing. After a slashing event has occurred in the NativeVault, Alice's validator looses all of its funds. Snapshot is started for Alice to reduce her assets by 32 ETH. `validateSnapshotProofs()` will calculate `balanceDeltaWei` as -32, subsequently calling `_updateSnapshot()` function.

[NativeVault.sol#L151-L159](https://github.com/karak-network/karak-arena-mitigations/blob/475cfd73744cabe239720feec4a227a739910119/src/NativeVault.sol#L151-L159)
```solidity
    int256 balanceDeltaWei = self.validateSnapshotProof(
        nodeOwner,
        validatorDetails,
        balanceContainer.containerRoot,
        balanceProofs[i]
    );
    snapshot.remainingProofs--;
    snapshot.balanceDeltaWei += balanceDeltaWei;
}
_updateSnapshot(node, snapshot, nodeOwner);
```

`_updateSnapshot()` calls `_updateBalance()`, where `_decreaseBalance()` function is invoked. `_decreaseBalance()` will burn all of Alice's shares and reduce `totalAssets` of the NativeVault by 32 ETH.

[NativeVault.sol#L511-L515](https://github.com/karak-network/karak-arena-mitigations/blob/475cfd73744cabe239720feec4a227a739910119/src/NativeVault.sol#L511-L515)
```solidity
uint256 shares = Math.min(convertToShares(assets), balanceOf(_of));
```

_Trimmed to 38 lines — full report: https://github.com/code-423n4/2024-09-karak-mitigation-findings/issues/16_
