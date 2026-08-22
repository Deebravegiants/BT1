# [M] EtherFiAdmin.sol::pause() function unusable

## Summary
Severity: Medium
Chain: Smart contract
Component: ether-fi
Published: 2023-11-08
Source: https://github.com/hats-finance/ether-fi-0x36c3b77853dec9c4a237a692623293223d4b9bc4/issues/31
Type: hats-finding

## Details
**Github username:** @erictee2802
**Submission hash (on-chain):** 0x585384659f41f160dbb8e8dc1cb52f227eec5e239c9139b308c93c981855af1e
**Severity:** medium

**Description:**
**Description**\
The function `EtherFiAdmin.sol::pause()` is unusable because of `onlyOwner` and `whenPaused` modifiers. 



**Attack Scenario**\
Let's suppose owner tries to pause only the `EtherFiOracle.sol` contract, he will call `EtherFiAdmin.sol::pause(true,false,false,false,false,false)`. However, the call will revert because of `onlyOwner` modifier. The only caller that can call the`EtherFiOracle.sol::pauseContract()` is the deployer of `EtherFiOracle.sol`. Even if it is called by the right user, the call will still revert because of `whenPaused` modifier in `PausableUpgradeable.sol`. This is because the contract `EtherFiAdmin.sol` tries to unpause the contracts in `else statement` even it is not paused status.

`EtherFiAdmin.sol::pause()`:

```
    function pause(bool _etherFiOracle, bool _stakingManager, bool _auctionManager, bool _etherFiNodesManager, bool _liquidityPool, bool _membershipManager) external isAdmin() {
        if (_etherFiOracle) {
            etherFiOracle.pauseContract();
        } else {
            etherFiOracle.unPauseContract();
        }
        if (_stakingManager) {
            stakingManager.pauseContract();
        } else {
            stakingManager.unPauseContract();
        }
        if (_auctionManager) {
            auctionManager.pauseContract();
        } else {
            auctionManager.unPauseContract();
        }
        if (_etherFiNodesManager) {
            etherFiNodesManager.pauseContract();
        } else {
            etherFiNodesManager.unPauseContract();
        }
        if (_liquidityPool) {
```

_Trimmed to 38 lines — full report: https://github.com/hats-finance/ether-fi-0x36c3b77853dec9c4a237a692623293223d4b9bc4/issues/31_
