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
            liquidityPool.pauseContract();
        } else {
            liquidityPool.unPauseContract();
        }
        if (_membershipManager) {
            membershipManager.pauseContract();
        } else {
            membershipManager.unPauseContract();
        }
    }
```



**Attachments**

1. **Proof of Concept (PoC) File**
```
// SPDX-License-Identifier: UNLICENSED
pragma solidity ^0.8.13;

import "./TestSetup.sol";
import "forge-std/console2.sol";

contract EtherFiAdminTest is TestSetup {

    function setUp() public {

        setUpTests();

    }


    function test_cannotPauseProperly() public {

        vm.startPrank(owner);
        etherFiAdminInstance.updateAdmin(owner,true);
        vm.expectRevert("Pausable: not paused");
        etherFiOracleInstance.unPauseContract();

        vm.expectRevert("Ownable: caller is not the owner");
        etherFiAdminInstance.pause(true,false,false,false,false,false); //@audit this will fails due to caller is not owner.
        vm.stopPrank();
    

    }

```

2. **Recommendations**
Check whether the contract(s) are in pause status first instead of directly calling `unpauseContract()` in the else statements.
