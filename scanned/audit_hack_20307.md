# [M] 5.2.14 WatcherManager is not set correctly

## Summary
Severity: Medium
Source: https://github.com/tintinweb/smart-contract-vulndb
Type: audit-issue

## Details
**Severity:** Medium Risk
**Context:** WatcherClient.sol#L36-L39
**Description:** ThesetWatcherManagerfunction missed to actually update thewatcherManager, instead it is just
emitting an event mentioning that Watcher Manager is updated when it is not.
This could become a problem once new modules are added/revised inWatcherManagercontract andWatcher-
Clientwants to use this upgradedWatcherManager.WatcherClientwill be forced to use the outdated Watcher-
Manager contract code.
**Recommendation:** Revise thesetWatcherManagerfunction as shown below:
function setWatcherManager(address _watcherManager) external onlyOwner {
require(_watcherManager != address(watcherManager), "already watcher manager");
+ watcherManager = WatcherManager(_watcherManager);
emit WatcherManagerChanged(_watcherManager);
}

**Connext:** Fixed in PR 2432.
**Spearbit:** Verified.
