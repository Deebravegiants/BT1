# [M] Single signer can disable `HoprNodeManagementModule`

## Summary
Severity: Medium
Chain: Smart contract
Component: SafeStaking-by-HOPR
Published: 2023-10-11
Source: https://github.com/hats-finance/SafeStaking-by-HOPR-0x607386df18b663cf5ee9b879fbc1f32466ad5a85/issues/27
Type: hats-finding

## Details
**Github username:** @0xfuje
**Submission hash (on-chain):** 0xc42262e4f11eeed7e0277029f551a59963b2c77f6e693c6f05ec8b2ddde92b62
**Severity:** medium

**Description:**
## Impact
`HoprNodeManagementModule` is disabled from `Safe`, makes essential functionality of `SafeStaking` inaccessible

## Description
Threshold is set to one at `Safe`'s initialization, this means a single signer can disable `HoprNodeManagementModule`: making core functionality of  `SafeStaking by HOPR` unusable. Even if threshold is set to higher, multiple signers can collude to disable the node management `module`.

`src/node-stake/NodeStakeFactory.sol` - `clone()` - (threshold of one at initialization)
```solidity
        bytes memory safeInitializer = abi.encodeWithSignature(
            "setup(address[],uint256,address,bytes,address,address,uint256,address)",
            admins,
            1, // threshold
            address(0),
            hex"00",
            SafeSuiteLib.SAFE_CompatibilityFallbackHandler_ADDRESS,
            address(0),
            0,
            address(0)
        );
```
Note that while registering or de-registering a node in `NodeSafeRegitry.sol` `ensureNodeIsSafeModuleMember()` is always called to make sure the module is registered, however after a node is registered (via `registerSafeByNode()`) the `HoprNodeManagementModule` can simply be disabled in `Safe` via `disableModule()`. The registry will still treat it as a registered node-safe combination and return `true` on calls made to `isNodeSafeRegistered()`.

`vendor/solidity/safe-contracts-1.4.1/contracts/base/ModuleManager.sol` - [`disableModule()`](https://github.com/hats-finance/SafeStaking-by-HOPR-0x607386df18b663cf5ee9b879fbc1f32466ad5a85/blob/master/vendor/solidity/safe-contracts-1.4.1/contracts/base/ModuleManager.sol#L63-L70)
```solidity
    function disableModule(address prevModule, address module) public authorized {
        // Validate module address and check that it corresponds to module index.
        require(module != address(0) && module != SENTINEL_MODULES, "GS101");
        require(modules[prevModule] == module, "GS103");
        modules[prevModule] = modules[module];
        modules[module] = address(0);
        emit DisabledModule(module);
    }
```


## Proof of Concept
1. navigate to `packages/ethereum/contracts/test/node-stake/NodeStakeFactory.t.sol`
2. import `ModuleManager` contract from `safe-contracts` in the top of the file:
```solidity
import { ModuleManager } from "safe-contracts/base/ModuleManager.sol";
```
3. copy and paste the below proof of concept inside `HoprNodeStakeFactoryTest` (includes a helper function to execute safe transactions)
4. run `forge test --match-test test_SafeDisableHoprModule -vvvv`
```solidity
    function test_SafeDisableHoprModule() public {
        address channels = 0x0101010101010101010101010101010101010101;
        address token = 0x1010101010101010101010101010101010101010;
        vm.mockCall(channels, abi.encodeWithSignature("token()"), abi.encode(token));
        
        // 3 admins at initialization
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

        // 1. node - safe combination is registered in NodeSafeRegistry via registerSafeByNode()
        // 2. admins[2] disables HoprNodeMagamentModule
        vm.startPrank(admins[2]);

        bytes32 r = bytes32(uint256(uint160(address(admins[2]))));
        // 2.1 - get transaction hash of disabling HoprNodeMagamentModule
        bytes32 dataHash = Safe(safe).getTransactionHash(
            safe, 0, abi.encodeWithSelector(ModuleManager.disableModule.selector, address(0x1), module),
            Enum.Operation.Call, 0, 0, 0, address(0), msg.sender, 1
        );
        // 2.2 - approve hash of disabling the module
        Safe(safe).approveHash(dataHash);

        // 2.3 - finally disable HoprNodeMagamentModule
        Safe(safe).execTransaction(
            safe,
            0,
            abi.encodeWithSelector(ModuleManager.disableModule.selector, address(0x1), module),
            Enum.Operation.Call,
            0,
            0,
            0,
            address(0),
            payable(address(msg.sender)),
            abi.encodePacked(abi.encode(r, bytes32(0), bytes1(hex"01")))
        );
    }
```

## Recommended Mitigation
Consider developing a `Safe Guard` contract to prevent disabling `HoprNodeManagementModule`. It can be enabled in `Safe` via `GuardManager.sol` - [`setGuard()`](https://github.com/hats-finance/SafeStaking-by-HOPR-0x607386df18b663cf5ee9b879fbc1f32466ad5a85/blob/master/vendor/solidity/safe-contracts-1.4.1/contracts/base/GuardManager.sol). The `guard` checks every transactions made with `Safe`.

`vendor/solidity/safe-contracts-1.4.1/contracts/Safe.sol` - `execTransaction()`
```solidity
	address guard = getGuard();
	...
	if (guard != address(0)) {
	    Guard(guard).checkAfterExecution(txHash, success);
	}
```

`checkAfterExecution()` of the `guard` should check if the `HoprNodeManagementModule` is still implemented after execution via querying from `ModuleManager.sol`of `Safe` and checking [`isModuleEnabled()`](https://github.com/hats-finance/SafeStaking-by-HOPR-0x607386df18b663cf5ee9b879fbc1f32466ad5a85/blob/master/vendor/solidity/safe-contracts-1.4.1/contracts/base/ModuleManager.sol#L131-L133).
