# [H] 5.1.10 Large number of inbound roots can DOS theRootManager

## Summary
Severity: High
Source: https://github.com/tintinweb/smart-contract-vulndb
Type: audit-issue

## Details
**Severity:** High Risk
**Context:** RootManager.sol#L154-L
**Description:** It is possible to perform a DOS against theRootManagerby exploiting thedequeueVerifiedfunction
orinsertfunction of theRootManager.sol.
The following describes the possible attack path:

1. Assume that a malicious user calls the permissionlessGnosisSpokeConnector.sendfunction 1000 times (or
    any number of times that will cause an Out-of-Gas error later) within a single transaction/block on Gnosis
    causing a large number of Gnosis's outboundRoots to be forwarded toGnosisHubConnectoron Ethereum.
2. Since the 1000 outboundRoots were sent at the same transaction/block earlier, all of them should arrive at
    theGnosisHubConnectorwithin the same block/transaction on Ethereum.


3. For each of the 1000 outboundRoots received, theGnosisHubConnector.processMessagefunction will be
    triggered to process it, which will in turn call theRootManager.aggregatefunction to add the received out-
    boundRoot into thependingInboundRootsqueue. As a result, 1000 outboundRoots with the samecommit-
    Blockwill be added to thependingInboundRootsqueue.
4. After the delay period, theRootManager.propagatefunction will be triggered. The function will call the
    dequeueVerifiedfunction to dequeue 1000 verified outboundRoots from thependingInboundRootsqueue
    by looping through the queue. This might result in an Out-of-Gas error and cause a revert.
5. If the abovedequeueVerifiedfunction does not revert, theRootManager.propagatefunction will attempt to
    insert 1000 verified outboundRoots to the aggregated Merkle tree, which might also result in an Out-of-Gas
    error and cause a revert.
If theRootManager.propagatefunction reverts when called, the latest aggregated Merkle root cannot be forwarded
to the spokes. As a result, none of the messages can be proven and processed on the destination chains.
Note: the processing on the Hub (which is on mainnet) can also become very expensive, as the mainnet usually
as a far higher gas cost than the Spoke.
**Recommendation:** Both solutions should be implemented to sufficiently mitigate this issue.
1. Place restrictions on the SpokeConnector'ssendfunction. Thesendfunction should be restricted so that the
domain's outbound root will only be forwarded to the hub when the following conditions are met:
- If the last root sent is different from the current root to be sent
- After the execution interval has lapsed (e.g. only able to trigger thesendfunction once every few
minutes) - This is to prevent a malicious user from bypassing the first measure (lastRootSent != out-
boundRoot) by sending a cheap message to trigger thedispatchfunction to change the outboundRoot
to a new one before calling thesendfunction
2. Bound the number of outbound roots that can be aggregated per call, and allow them to be processed in
batches (if needed)
**Connext:** Solved in PR 2199 and PR 2545.
**Spearbit:** Verified.
