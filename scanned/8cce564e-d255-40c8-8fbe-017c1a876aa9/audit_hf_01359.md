# [M] WatcherManager is not set correctly

## Summary
Severity: Medium
Contest weight: 0.3789
Dataset id: 6851
Source: https://huggingface.co/datasets/Zaevlad/audit-findings-dataset
Type: audit-finding

## Details
The setWatcherManager function missed to actually update the watcherManager, instead it is just emitting an event mentioning that Watcher Manager is updated when it is not.
This could become a problem once new modules are added/revised in WatcherManager contract and WatcherClient wants to use this upgraded WatcherManager. WatcherClient will be forced to use the outdated WatcherManager contract code.

## Recommendation
Revise the setWatcherManager function as shown below:
```solidity
function setWatcherManager(address _watcherManager) external onlyOwner {
    require(_watcherManager != address(watcherManager), "already watcher manager");
    watcherManager = WatcherManager(_watcherManager);
    emit WatcherManagerChanged(_watcherManager);
}
```
