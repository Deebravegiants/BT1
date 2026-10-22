# [H] keep-core - reportRelayEntryTimeout creates an incentive for nodes to race for rewards potentially wasting gas and it creates an opportunity for front-running

## Summary
Severity: High
Source: https://github.com/tintinweb/smart-contract-vulndb
Type: audit-issue

## Details
#### Description

The incentive on `reportRelayEntryTimeout` for being rewarded with 5% of the seized amount creates an incentive to call the method but might also kick off a race for front-running this call. This method is being called from the keep node which is unlikely to adjust the gasPrice and might always lose the race against a front-running bot collecting rewards for all timeouts and fraud proofs (41) 


#### Examples


**keep-core/contracts/solidity/contracts/KeepRandomBeaconOperator.sol:L600-L626**
```solidity
/**
 * @dev Function used to inform about the fact the currently ongoing
 * new relay entry generation operation timed out. As a result, the group
 * which was supposed to produce a new relay entry is immediately
 * terminated and a new group is selected to produce a new relay entry.
 * All members of the group are punished by seizing minimum stake of
 * their tokens. The submitter of the transaction is rewarded with a
 * tattletale reward which is limited to min(1, 20 / group_size) of the
 * maximum tattletale reward.
 */
function reportRelayEntryTimeout() public {
    require(hasEntryTimedOut(), "Entry did not time out");
    groups.reportRelayEntryTimeout(signingRequest.groupIndex, groupSize, minimumStake);

    // We could terminate the last active group. If that's the case,
    // do not try to execute signing again because there is no group
    // which can handle it.
    if (numberOfGroups() > 0) {
        signRelayEntry(
            signingRequest.relayRequestId,
            signingRequest.previousEntry,
            signingRequest.serviceContract,
            signingRequest.entryVerificationAndProfitFee,
            signingRequest.callbackFee
        );
    }
}
```

#### Recommendation

Make sure that `reportRelayEntryTimeout` throws as early as possible if the group was previously terminated (`isGroupTerminated`) to avoid that keep-nodes spend gas on a call that will fail. Depending on the reward for calling out the timeout this might create a front-running opportunity that cannot be resolved.
