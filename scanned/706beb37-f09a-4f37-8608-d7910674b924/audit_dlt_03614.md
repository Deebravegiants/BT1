# [H] H-02 Unmitigated

## Summary
Severity: High
Chain: Smart contract
Component: 2024-09-karak-mitigation
Published: 2024-09-15
Source: https://github.com/code-423n4/2024-09-karak-mitigation-findings/issues/12
Type: code-finding

## Details
# Lines of code

https://github.com/karak-network/karak-arena-mitigations/blob/475cfd73744cabe239720feec4a227a739910119/src/Core.sol#L171-L178
https://github.com/karak-network/karak-arena-mitigations/blob/475cfd73744cabe239720feec4a227a739910119/src/entities/CoreLib.sol#L118-L147
https://github.com/karak-network/karak-arena-mitigations/blob/475cfd73744cabe239720feec4a227a739910119/src/entities/CoreLib.sol#L89-L116
https://github.com/karak-network/karak-arena-mitigations/blob/475cfd73744cabe239720feec4a227a739910119/src/NativeVault.sol#L46-L77


# Vulnerability details

## C4 Issue: 
H-02: https://github.com/code-423n4/2024-07-karak-findings/issues/55

## Comments
Before mitigation when deploying a new NativeVault operator could set `manager`, `slashStore` and `nodeImplementation` to anything. This happened because `vaultConfig.extraData` lacked input validation when calling `deployVaults()`. The impacts of the original issue were the ability of operator to create a NativeVault that can be silently unslashable and escalate his rights, obtaining a privileged role that will allow him to steal user's funds. 

## Mitigation
[FIX](https://github.com/karak-network/karak-arena-mitigations/commit/fdef9d25e2b7c0a528d5a6dfcce64a3a518165af#diff-940446432243a929cd0f5ea691c4e90d60ee655723e2d5d8fcafc7b7504cfe98L59-R61)
The mitigation removes the `slashStore` variable altogether and `NativeVault` burns the slashed ETH directly by itself. The current mitigation does not address all of the impacts of the original issue. As currently operator can still escalate his rights and steal user's funds.

## Proof Of Concept
As can be seen, when `deployVaults()` is called with `vaultConfigs` passed by an operator, the variables is passed to `createVault()` unvalidated.

[CoreLib.sol#L133-L141](https://github.com/karak-network/karak-arena-mitigations/blob/475cfd73744cabe239720feec4a227a739910119/src/entities/CoreLib.sol#L133-L141)
```solidity
IKarakBaseVault vault = createVault(
    self,
    operator,
    vaultConfigs[i].asset,
    vaultConfigs[i].name,
    vaultConfigs[i].symbol,
    vaultConfigs[i].extraData,
    implementation
);
```

After cloning a vault, `createVault` initializes it with the configuration passed by the operator.


_Trimmed to 38 lines — full report: https://github.com/code-423n4/2024-09-karak-mitigation-findings/issues/12_
