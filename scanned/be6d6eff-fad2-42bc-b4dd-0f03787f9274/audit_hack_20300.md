# [H] 5.1.11 MissingmirrorConnectorcheck on Optimism hub connector

## Summary
Severity: High
Source: https://github.com/tintinweb/smart-contract-vulndb
Type: audit-issue

## Details
**Severity:** High Risk
**Context:** OptimismHubConnector.sol#L69-L
**Description:** processMessageFromRoot()calls_processMessage()to process messages for the "fast" path. But
_processMessage()can also be called by the AMB in the slow path.
The second call to_processMessage()is not necessary (and could double process the message, which luckily
is prevented via theprocessed[]mapping). The second call (from the AMB directly to_processMessage()) also
doesn't properly verify the origin of the message, which might allow the insertion of fraudulent messages.


```
function processMessageFromRoot(...) ... {
_processMessage(abi.encode(_data));
}
function _processMessage(bytes memory _data) internal override {
// sanity check root length
require(_data.length == 32, "!length");
// get root from data
bytes32 root = bytes32(_data);
if (!processed[root]) {
// set root to processed
processed[root] = true;
// update the root on the root manager
IRootManager(ROOT_MANAGER).aggregate(MIRROR_DOMAIN, root);
}// otherwise root was already sent to root manager
}
```
**Recommendation:** Remove the second path.
**Connext:** Solved in PR 2447.
**Spearbit:** Verified.
