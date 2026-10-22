# [M] Removing pools with swapAndPop() in EulerSwapFactory.uninstall() corrupts stored indexes

## Summary
Severity: Medium
Contest weight: 0.5940
Dataset id: 5212
Source: https://huggingface.co/datasets/Zaevlad/audit-findings-dataset
Type: audit-finding

## Details
When deploying a new pool, the index of the pool's address in the allPools and poolMap arrays are stored:
eulerAccountState[eulerAccount] = EulerAccountState({
pool: newOperator,
allPoolsIndex: uint48(allPools.length),
poolMapIndex: uint48(poolMapArray.length)
});
When uninstalling a pool with uninstall(), swapAndPop() is used to remove pool addresses from the allPools/poolMap array:
```solidity
function swapAndPop(address[] storage arr, uint256 index) internal {
    arr[index] = arr[arr.length - 1];
    arr.pop();
}
```
However, this causes the index stored in eulerAccountState for the last pool address to become incorrect.
For example:
• Assume two pools are installed, so allPools = [0x11, 0x22].
• For the second pool, allPoolsIndex = 1.
• The first pool is uninstalled, so allPools = [0x22].
• Since allPoolsIndex is not updated, it is now invalid.
When the second pool is uninstalled, it will remove the wrong index in the allPools array. As a result, it will be impossible for accounts to uninstall pools. The following proof of concept demonstrates how the second pool cannot be uninstalled due to an OOB access:
```solidity
// SPDX-License-Identifier: GPL-2.0-or-later
pragma solidity ^0.8.24;
import "forge-std/Test.sol";
import {EulerSwapTestBase, IEulerSwap} from "test/EulerSwapTestBase.t.sol";
contract EulerSwapFactoryTest is EulerSwapTestBase {
    function test_multipleUninstalls() public {
        // Users
        address alice = makeAddr("alice");
        address bob = makeAddr("bob");
        // Parameters for deployPool()
        IEulerSwap.Params memory params = getEulerSwapParams(1e18, 1e18, 1e18, 1e18, 0, 0, 0, 0, address(0));
        IEulerSwap.InitialState memory initialState = IEulerSwap.InitialState(1e18, 1e18);
        bytes32 salt = bytes32(0);
        // Deploy pool for Alice
        params.eulerAccount = alice;
        address alicePool = eulerSwapFactory.computePoolAddress(params, salt);
        vm.startPrank(alice);
        evc.setAccountOperator(alice, alicePool, true);
        eulerSwapFactory.deployPool(params, initialState, salt);
        // Deploy pool for Bob
        params.eulerAccount = bob;
        address bobPool = eulerSwapFactory.computePoolAddress(params, salt);
        vm.startPrank(bob);
        evc.setAccountOperator(bob, bobPool, true);
        eulerSwapFactory.deployPool(params, initialState, salt);
        // Uninstall pool for Alice
        vm.startPrank(alice);
        evc.setAccountOperator(alice, alicePool, false);
        eulerSwapFactory.uninstallPool();
        // Uninstalling pool for Bob reverts due to an OOB access of the allPools array
        vm.startPrank(bob);
        evc.setAccountOperator(bob, bobPool, false);
        vm.expectRevert(stdError.indexOOBError);
        eulerSwapFactory.uninstallPool();
    }
}
```

## Recommendation
Consider storing pools with OpenZeppelin's EnumerableSet instead of arrays. The pools can be removed from the set based on their address instead of index.
