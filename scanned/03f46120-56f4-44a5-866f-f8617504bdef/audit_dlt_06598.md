# [H] V1 Profiles Can Avoid Penalties Using `transferHumanity`

## Summary
Severity: High
Chain: Smart contract
Component: Proof-Of-Humanity-V2
Published: 2024-08-31
Source: https://github.com/hats-finance/Proof-Of-Humanity-V2-0xef0709445d394a22704850c772a28a863bb780b0/issues/134
Type: hats-finding

## Details
**Github username:** --
**Twitter username:** --
**Submission hash (on-chain):** 0xe5dc4705e84915d0e5acbc15c722ad7b64240a024498f42039f03f3ec27416d4
**Severity:** high

**Description:**
**Description**  
V1 users can bypass the entire vouching, challenge, and appeal process by transferring their humanity to another chain using the `CrossChainProofOfHumanity::transferHumanity` function. In contrast, when claiming or renewing their humanity through the `ProofOfHumanityExtended` contract’s `claimHumanity` or `renewHumanity` functions, V1 users must go through the entire claiming process.

The `CrossChainProofOfHumanity::transferHumanity` function can be invoked by users of any Proof of Humanity (PoH) version. This function calls `ProofOfHumanityExtended::ccDischargeHumanity` to remove the owner of the humanity record. The issue arises because V1 users can directly call this function to switch chains:

```solidity
        if (humanity.owner == _account && block.timestamp < humanity.expirationTime) {
            require(!humanity.vouching);

            expirationTime = humanity.expirationTime;

            delete humanity.owner;
        } else {
            // V1 profiles have default humanity.
            humanityId = bytes20(_account);

            // Should revert in case account is not registered.
@>            expirationTime = forkModule.tryRemove(_account);
        }
```

If a V1 user has not created a profile on POHv2, the state variables in the `ProofOfHumanityExtended` contract corresponding to v1 users will lack complete data. The `accountHumanity` variable, in particular, will be unset for V1 profiles that have not created humanity on POHv2. This variable is used in the `ccDischargeHumanity` function, which will always have a `0` humanityId for all V1 humanity profiles that lack a V2 profile:
```solidity
    function ccDischargeHumanity(
        address _account
    ) external onlyCrossChain returns (bytes20 humanityId, uint40 expirationTime) {
@>        humanityId = accountHumanity[_account];
@>        Humanity storage humanity = humanityData[humanityId];
```

As the `0` humanityId remains unassigned, the corresponding `humanityData` variable will have no data. Consequently, whenever a V1 user calls `ccDischargeHumanity` without creating a V2 humanity, their `humanityData` will contain only default data.


_Trimmed to 38 lines — full report: https://github.com/hats-finance/Proof-Of-Humanity-V2-0xef0709445d394a22704850c772a28a863bb780b0/issues/134_
