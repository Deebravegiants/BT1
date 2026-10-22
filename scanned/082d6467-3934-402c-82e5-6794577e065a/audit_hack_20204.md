# [H] 5.2.6 DOS attack on the NomadHome.solContract

## Summary
Severity: High
Source: https://github.com/tintinweb/smart-contract-vulndb
Type: audit-issue

## Details
**Severity:** High Risk
**Context:** Home.sol#L332, Queue.sol#L119-L
**Description:** Upon callingxcall(), a message is dispatched via Nomad. A hash of this message is inserted
into the merkle tree and the new root will be added at the end of the queue. Whenever the updater ofHome.sol
commits to a new root,improperUpdate()will check that the new update is not fraudulent. In doing so, it must
iterate through the queue of merkle roots to find the correct committed root. Because anyone can dispatch a
message and insert a new root into the queue it is possible to impact the availability of the protocol by preventing
honest messages from being included in the updated root.
function improperUpdate(..., bytes32 _newRoot, ... ) public notFailed returns (bool) {
...
// if the _newRoot is not currently contained in the queue,
// slash the Updater and set the contract to FAILED state
if (!queue.contains(_newRoot)) {
_fail();
...
}
...
}
function contains(Queue storage _q, bytes32 _item) internal view returns (bool) {
for (uint256 i = _q.first; i <= _q.last; i++) {
if (_q.queue[i] == _item) {
return true;
}
}
return false;
}

**Recommendation:** Consider altering the queuing system such thatimproperUpdate()takes in an index argument
that is greater than the old root. By specifying the index we can check that the new root is valid in O(1) time instead
of O(n) time. Alternatively, it may be better to remove the queuing system altogether.
**Connext:** This is discussed in the Nomad Quantstamp audit report, and will be addressed by removing the queue
for messaging in a future upgrade. Going to leave this issue open, though will note that this attack is costly to
perform and (currently) exists within the Nomad protocol.


**Spearbit:** Acknowledged.
