# [H] Humanity Revocation Ineffective Due to Incorrect `pendingRevocation` Handling in `executeRequest` function

## Summary
Severity: High
Chain: Smart contract
Component: Proof-Of-Humanity-V2
Published: 2024-08-31
Source: https://github.com/hats-finance/Proof-Of-Humanity-V2-0xef0709445d394a22704850c772a28a863bb780b0/issues/119
Type: hats-finding

## Details
**Github username:** --
**Twitter username:** --
**Submission hash (on-chain):** 0xb70d3516ff1946d9312533ba42bd0b9845248ce4bd25fb365f41cd2de491aa11
**Severity:** high

**Description:**
**Description**\
In the `executeRequest` function of the `ProofOfHumanityExtended` contract, if a revocation request is processed and the current timestamp is greater than the user's expiration time, the user's humanity is not deleted, and the `pendingRevocation` variable is not set to `false`:
```solidity
if (request.revocation) {
    if (humanity.owner != address(0x0) && block.timestamp < humanity.expirationTime) {
        delete humanity.owner;
@>        humanity.pendingRevocation = false;

        // If not claimed in this contract, directly remove in fork module.
    } else forkModule.remove(address(_humanityId));

    emit HumanityRevoked(_humanityId, _requestId);
```

According to this logic, if the current timestamp is beyond the humanity's expiration time, there is no need to delete the owner since the humanity has already expired. While this is logically correct, the issue arises because `pendingRevocation` is also not set to `false` in this scenario.

When a revocation request is submitted via the `revokeHumanity` function, a request is created with the `challengePeriodStart` variable set to the current timestamp:
```solidity
request.challengePeriodStart = uint40(block.timestamp);
```

A user can only call the `executeRequest` function after the challenge period has ended, as enforced by the following check:
```solidity
require(request.challengePeriodStart + challengePeriodDuration < block.timestamp);
```

If `challengePeriodStart` plus `challengePeriodDuration` is greater than the humanity's expiration time, the user's `humanity.owner` will not be deleted, and `humanity.pendingRevocation` will not be set to `false`.

Therefore, if a revocation request is made such that the challenge period ends after the user's expiration time, `humanity.pendingRevocation` will remain `true`. 

If this user subsequently submits a legitimate request to re-enter the registry after expiration and enters the registry, their humanity can no longer be revoked due to `humanity.pendingRevocation` already being `true`. This is enforced by the following check in the `revokeHumanity` function:


_Trimmed to 38 lines — full report: https://github.com/hats-finance/Proof-Of-Humanity-V2-0xef0709445d394a22704850c772a28a863bb780b0/issues/119_
