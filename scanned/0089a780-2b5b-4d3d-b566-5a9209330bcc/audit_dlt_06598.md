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

This loophole allows V1 users with pending requests to switch chains and retain their humanity, as this condition is always satisfied:

```solidity
        require(humanity.nbPendingRequests == 0);
```

Since any V1 humanity user’s `humanityData` will contain default values, the `humanity.nbPendingRequests` variable will always default to `0`.

Moreover, since V1 users without a POHv2 profile will have the `humanity.owner` set to `0x0`, this section of code will never execute:

```solidity
        if (humanity.owner == _account && block.timestamp < humanity.expirationTime) {
            require(!humanity.vouching);

            expirationTime = humanity.expirationTime;

            delete humanity.owner;
        } else {
```

Instead, the following block will execute, calling the `forkModule::tryRemove` function:

```solidity
        } else {
            // V1 profiles have default humanity.
            humanityId = bytes20(_account);

            // Should revert in case account is not registered.
            expirationTime = forkModule.tryRemove(_account);
        }
```

The `forkModule` contract’s `tryRemove` function only checks four conditions:
1. Whether the V1 humanity is registered.
2. If the V1 humanity has expired.
3. Whether the V1 humanity was created before the fork time.
4. That it is not removed from the ForkModule.

This function does not check other critical indicators such as request count, pending requests, vouch status, or humanity status, leading to inconsistent data in POHv2.

As a result, any V1 user without a V2 profile on POHv2 can switch chains via `ccDischargeHumanity` as long as their humanity on V1 is registered, not expired, created before the fork time and not removed from the ForkModule. The has several adverse effects:

1. **Avoiding Revocation Requests on POHv1**: A V1 user facing a revocation request on POHv1 can call the `transferHumanity` function before the `rule` or `executeRequest` functions are called, switching chains and retaining their humanity on the new chain, thereby avoiding revocation. This is possible because there is no check for the `requests.length` in the whole transfer process.

2. **Avoiding Vouch Penalties on POHv1**: A V1 user penalized for malicious vouching on POHv1 can invoke the `transferHumanity` function before the `processVouches` function is called, switch chains, and retain their humanity on the new chain, effectively avoiding penalties. This is possible because there is no check for the `hasVouched` status in the whole transfer process.

Additionally, in POHv2, the `accountHumanity` variable is only set when a user claims or renews humanity through the `_requestHumanity` function:

```solidity
        accountHumanity[msg.sender] = _humanityId;
```

Therefore, V1 users who do not create a V2 profile will have their `accountHumanity` set to `0` by default.

1. **Avoiding Revocation Requests on POHv2**: If a revocation request is made against a V1 user on POHv2 using `revokeHumanity` function in `ProofOfHumanityExtended` contract, the `humanityData` updated during in this function will use the V1 user’s default `humanityId`, which is their address. While logically correct, the issue arises with the `ccDischargeHumanity` function. Since this function retrieves the humanityId from the `accountHumanity` variable, all V1 users will have a default humanityId of `0` if they did not create humanity on v2. As a result, V1 users can switch chains using `transferHumanity` even if a revocation request is active against them, effectively avoiding revocation.

2. **Avoiding Vouch Penalties on POHv2**: Similar to point 3, the `humanityData` for a V1 user is updated using the default `humanityId` when `processVouches` function is called, which is their address. However, in the `ccDischargeHumanity` function, a V1 user retrieves the humanity data for the `0` humanityId, which is empty by default. This allows V1 users to switch chains using `transferHumanity` before `processVouches` function is called even if they face penalties for malicious vouching, effectively avoiding the penalty.

In all these cases, V1 humanity users can circumvent penalties.

**Mitigation**  
1. Remove the `accountHumanity` variable line in the `ccDischargeHumanity` function and use the `humanityId` directly:

```solidity
    function ccDischargeHumanity(
--        address _account
++        bytes20 _humanityId
    ) external onlyCrossChain returns (bytes20 humanityId, uint40 expirationTime) {
--        humanityId = accountHumanity[_account];
--        Humanity storage humanity = humanityData[humanityId];
++        Humanity storage humanity = humanityData[_humanityId];
```

2. Prevent V1 users from directly calling the `transferHumanity` function. V1 users should first create a V2 profile before being allowed to switch chains.
