# [H] Possibility of Holding Humanity ID in Both Chains After Renewal and Transfer

## Summary
Severity: High
Chain: Smart contract
Component: Proof-Of-Humanity-V2
Published: 2024-08-31
Source: https://github.com/hats-finance/Proof-Of-Humanity-V2-0xef0709445d394a22704850c772a28a863bb780b0/issues/126
Type: hats-finding

## Details
**Github username:** @0xmahdirostami
**Twitter username:** 0xmahdirostami
**Submission hash (on-chain):** 0xbc9ed567305f76c56a4b53d876dd0b9c8a8e019d96fe0d89092fe69bda4892c6
**Severity:** high

**Description:**
### Summary
A vulnerability exists where a V1 user, after renewing their Humanity ID, can hold the same Humanity ID on both V1 and V2 contracts simultaneously, potentially leading to the creation of illegitimate Humanity IDs across multiple chains and difficulties in revoking these IDs.


### Vulnerability Detail

**Renew Humanity:** A V1 user calls `ProofOfHumanityExtented::renewHumanity`, which allows them to extend their Humanity ID's expiration time on the V2.
So after gaining humanity in the v2 contract, the user has humanity on v1 and v2 simultaneously.


**Transfer Humanity:** The user can then call `transferHumanity`, which invokes the `ProofOfHumanityExtented::ccDischargeHumanity` function.
```solidity
function ccDischargeHumanity(
        address _account
    ) external onlyCrossChain returns (bytes20 humanityId, uint40 expirationTime) {
        humanityId = accountHumanity[_account];
        Humanity storage humanity = humanityData[humanityId];
        require(humanity.nbPendingRequests == 0);

        if (humanity.owner == _account && block.timestamp < humanity.expirationTime) {
            require(!humanity.vouching);

            expirationTime = humanity.expirationTime;

            delete humanity.owner;
        } else {
            // V1 profiles have default humanity.
            humanityId = bytes20(_account);

            // Should revert in case account is not registered.
            expirationTime = forkModule.tryRemove(_account);
        }

        emit HumanityDischargedDirectly(humanityId);
    }
```
so after the transfer, he still holds the v1 humanity.
now he holds humanity in the target chain and source chain simultaneously. (he could call a second transfer, and hold humanity in two target chains).



**Revoke humanity:** Another impact of having humanity ID in v1 and v2 is that humanity will not revoked by one revoke request.
```solidity
        if (request.revocation) {
            humanity.pendingRevocation = false;

            if (resultRuling == Party.Requester) {
                if (humanity.owner != address(0x0) && block.timestamp < humanity.expirationTime)
                    delete humanity.owner;
                    // If not claimed in this contract, remove in fork module.
                else forkModule.remove(address(disputeData.humanityId));

```


### Impact
- Illegitimate Humanity IDs: The vulnerability allows V1 users to hold the same Humanity ID on multiple chains.

- Revocation Issues: This vulnerability makes humanity IDs not being revoked by one revoke request
