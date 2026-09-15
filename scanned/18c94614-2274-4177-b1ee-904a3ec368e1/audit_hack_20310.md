# [M] 5.2.18 Absence of Minimum delayBlocks

## Summary
Severity: Medium
Source: https://github.com/tintinweb/smart-contract-vulndb
Type: audit-issue

## Details
**Severity:** Medium Risk
**Context:** RootManager.sol#L102-106, SpokeConnector.sol#L218-L221
**Description:** Owner can accidentally setdelayBlocksas 0 (or a very small delay block) which will collapse the
whole fraud protection mechanism. Since there is no check for minimum delay before setting a new delay value so
even a low value will be accepted bysetDelayBlocksfunction
function setDelayBlocks(uint256 _delayBlocks) public onlyOwner {
require(_delayBlocks != delayBlocks, "!delayBlocks");
emit DelayBlocksUpdated(_delayBlocks, delayBlocks);
delayBlocks = _delayBlocks;
}

**Recommendation:** Introduce a variableminDelaywhich tells the minimum possible delay allowed by the contract.
Any attempt to change delay value usingsetDelayBlocksfunction should ensure that new delay is larger/equal to
minDelay
**Connext:** We could add a minimum for when delayBlocks is not 0, but that minimum will vary by chain / block
time, so that minimum HAS to be configurable. We could add a separate configuration endpoint and make it so it
takes 72 hours to change the delay blocks minimum, but that feels more like DAO functionality/responsibility. For
that reason, going with "acknowledged". At the very least, users can visibly check what the delayBlocks are set to
on-chain to make sure it's reasonable.
**Spearbit:** Acknowledged
