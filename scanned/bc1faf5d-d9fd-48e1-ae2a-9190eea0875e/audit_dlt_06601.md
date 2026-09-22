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

```solidity
function revokeHumanity(bytes20 _humanityId, string calldata _evidence) external payable {
    Humanity storage humanity = humanityData[_humanityId];

    require(
        (humanity.owner != address(0x0) && block.timestamp < humanity.expirationTime) ||
            // If not claimed on this contract check on V1.
            forkModule.isRegistered(address(_humanityId))
    );
@>    require(!humanity.pendingRevocation);
    require(humanity.lastFailedRevocationTime.addCap40(failedRevocationCooldown) < block.timestamp);

    uint256 requestId = humanity.requests.length;

    Request storage request = humanity.requests.push();
```

This means that any revocation request that is made at a time when the challenge period ends after the user's expiration time, the user can create a profile that cannot be revoked.

**Scenario**  
1. Alice's behavior raises concerns, and a user, Bob decides to initiate a revocation request against her.
2. Bob submits a revocation request through the `revokeHumanity` function, which sets the request's `challengePeriodStart` to the current timestamp (`block.timestamp`).
3. The challenge period eventually ends, but by this time, Alice’s humanity has already expired (`block.timestamp > humanity.expirationTime`).
4. Bob or any other user calls `executeRequest` to process the revocation request.
5. In the `executeRequest` function, the contract checks if the humanity has expired. Since Alice’s humanity has already expired (`block.timestamp > humanity.expirationTime`), the function does not delete `humanity.owner`, and crucially, does not set `humanity.pendingRevocation` to `false`.
6. Alice re-applies to register in the `ProofOfHumanityExtended` registry after her previous registration has expired. Now, because `humanity.pendingRevocation` was not set to `false` in the earlier revocation process, it remains `true` despite her new registration.
7. When another user tries to initiate a revocation against Alice after her re-entry, the `revokeHumanity` function reverts. Since `pendingRevocation` is still `true`, the function prevents any new revocation requests against Alice, effectively making her immune to future revocations.

**Mitigation**  
Modify the `executeRequest` function to set `pendingRevocation` to `false` regardless of whether the humanity has expired:

```solidity
function executeRequest(bytes20 _humanityId, uint256 _requestId) external {
    Humanity storage humanity = humanityData[_humanityId];
    Request storage request = humanity.requests[_requestId];
    require(request.status == Status.Resolving);
    require(request.challengePeriodStart + challengePeriodDuration < block.timestamp);

    if (request.revocation) {
        if (humanity.owner != address(0x0) && block.timestamp < humanity.expirationTime) {
--            humanity.pendingRevocation = false;
            delete humanity.owner;
        } else {
            forkModule.remove(address(_humanityId));
        }
++        humanity.pendingRevocation = false;
        emit HumanityRevoked(_humanityId, _requestId);
    } else if (!request.punishedVouch) {
        humanity.owner = request.requester;
        humanity.expirationTime = uint40(block.timestamp).addCap40(humanityLifespan);

        emit HumanityClaimed(_humanityId, _requestId);
    }

    humanity.nbPendingRequests--;
    request.status = Status.Resolved;
    delete humanity.requestCount[request.requester];

    if (request.vouches.length != 0) processVouches(_humanityId, _requestId, VOUCHES_TO_AUTOPROCESS);

    withdrawFeesAndRewards(request.requester, _humanityId, _requestId, 0, 0); // Automatically withdraw for the requester.
}
```
