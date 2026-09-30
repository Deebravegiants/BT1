# [M] The Factory administrator can upgrade frozen Proxies through upgrading the Factory implementation

## Summary
Severity: Medium
Contest weight: 0.5918
Dataset id: 10552
Source: https://huggingface.co/datasets/Zaevlad/audit-findings-dataset
Type: audit-finding

## Details
Currently, in a project created through Morpheus Factory contracts, the Distribution, L1Sender, L2MessageReceiver, and L2TokenReceiver contracts are deployed behind a FreezableBeaconProxy. The FreezableBeaconProxy allows the Factory to access the functions FreezableBeaconProxy.freeze() and FreezableBeaconProxy.unfreeze(), which are intended to allow the project deployer to opt in or out of Beacon upgrades. The current implementation of Factory allows only the project deployer of a project to call Factory.freezePool() and Factory.unfreezePool(). However, the Factory administrator can upgrade Factory to an implementation that allows arbitrary access to Factory.freezePool() and Factory.unfreezePool(), thereby gaining access to any project's FreezableBeaconProxy.freeze() and FreezableBeaconProxy.unfreeze() functions. This means that any project deployer, regardless of whether they have their FreezableBeaconProxy frozen or not, can have their Distribution, L1Sender, L2MessageReceiver, and L2TokenReceiver contracts forced to undergo a Beacon upgrade to an arbitrary implementation set by the Factory administrator. Recommendation: A potential remedy would be to remove the upgradeability of the Factory contract. Another option to consider would be to allow the deployment owner to grant and revoke privileges from the factory, however, this alters the balance of privilege between the project deployer and project owner.
Here are the changes to remove upgradeability.
Changes to Factory.sol.
```solidity
@@ -2,9 +2,9 @@
pragma solidity ^0.8.20;
import {Create2} from "@openzeppelin/contracts/utils/Create2.sol";
-import {UUPSUpgradeable} from "@openzeppelin/contracts-upgradeable/proxy/utils/UUPSUpgradeable.sol";
-import {OwnableUpgradeable} from "@openzeppelin/contracts-upgradeable/access/OwnableUpgradeable.sol";
-import {PausableUpgradeable} from "@openzeppelin/contracts-upgradeable/security/PausableUpgradeable.sol";
+import {Ownable} from "@openzeppelin/contracts/access/Ownable.sol";
+import {Pausable} from "@openzeppelin/contracts/security/Pausable.sol";
+
import {UpgradeableBeacon} from "@openzeppelin/contracts/proxy/beacon/UpgradeableBeacon.sol";
import {DynamicSet} from "@solarity/solidity-lib/libs/data-structures/DynamicSet.sol";
@@ -13,7 +13,7 @@ import {Paginator} from "@solarity/solidity-lib/libs/arrays/Paginator.sol";
import {IFactory} from "../interfaces/factories/IFactory.sol";
import {IFreezableBeaconProxy, FreezableBeaconProxy} from "../proxy/FreezableBeaconProxy.sol";
-abstract contract Factory is IFactory, OwnableUpgradeable, PausableUpgradeable, UUPSUpgradeable {
+abstract contract Factory is IFactory, Ownable, Pausable {
using DynamicSet for DynamicSet.StringSet;
using Paginator for DynamicSet.StringSet;
@@ -26,8 +26,6 @@ abstract contract Factory is IFactory, OwnableUpgradeable, PausableUpgradeable,
mapping(address deployer => mapping(string protocol => mapping(string poolType => address))) private _proxyPools;
mapping(address deployer => DynamicSet.StringSet) private _protocols;
function __Factory_init() internal onlyInitializing {}
/**
* @notice Returns contract to normal state.
*/
function _authorizeUpgrade(address) internal view override onlyOwner {}
}
```
Changes to L1Factory.sol.
```solidity
@@ -19,16 +19,7 @@ contract L1Factory is IL1Factory, Factory {
ArbExternalDeps public arbExternalDeps;
LzExternalDeps public lzExternalDeps;
constructor() {
_disableInitializers();
}
function L1Factory_init() external initializer {
__Pausable_init();
__Ownable_init();
__UUPSUpgradeable_init();
__Factory_init();
}
+
constructor() {}
function setDepositTokenExternalDeps(
DepositTokenExternalDeps calldata depositTokenExternalDeps_
@@ -38,20 +29,17 @@ contract L1Factory is IL1Factory, Factory {
depositTokenExternalDeps = depositTokenExternalDeps_;
}
function setLzExternalDeps(LzExternalDeps calldata lzExternalDeps_) external onlyOwner {
require(lzExternalDeps_.endpoint != address(0), "L1F: invalid LZ endpoint");
require(lzExternalDeps_.destinationChainId != 0, "L1F: invalid chain ID");
lzExternalDeps = lzExternalDeps_;
}
function setArbExternalDeps(ArbExternalDeps calldata arbExternalDeps_) external onlyOwner {
require(arbExternalDeps_.endpoint != address(0), "L1F: invalid ARB endpoint");
arbExternalDeps = arbExternalDeps_;
}
function setFeeConfig(address feeConfig_) external onlyOwner {
require(feeConfig_ != address(0), "L1F: invalid fee config");
```
Changes to L2Factory.sol.
```solidity
@@ -19,16 +19,7 @@ contract L2Factory is IL2Factory, Factory {
mapping(address deployer => mapping(string protocol => address)) private _mor20;
constructor() {
_disableInitializers();
}
function L2Factory_init() external initializer {
__Pausable_init();
__Ownable_init();
__UUPSUpgradeable_init();
__Factory_init();
}
+
constructor() {}
function setLzExternalDeps(LzExternalDeps calldata lzExternalDeps_) external onlyOwner {
require(lzExternalDeps_.endpoint != address(0), "L2F: invalid LZ endpoint");
@@ -37,7 +28,6 @@ contract L2Factory is IL2Factory, Factory {
lzExternalDeps = lzExternalDeps_;
}
function setUniswapExternalDeps(UniswapExternalDeps calldata uniswapExternalDeps_) external onlyOwner {
require(uniswapExternalDeps_.router != address(0), "L2F: invalid UNI router");
require(uniswapExternalDeps_.nonfungiblePositionManager != address(0), "L2F: invalid NPM");
```
Changes to IL1Factory.sol.
```solidity
@@ -73,7 +73,6 @@ interface IL1Factory {
/**
* The function that initializes the contract.
*/
function L1Factory_init() external;
/**
* The function to get fee config address.
```
Changes to IL2Factory.sol.
```solidity
@@ -66,7 +66,6 @@ interface IL2Factory {
/**
* The function that initializes the contract.
*/
function L2Factory_init() external;
/**
* The function that sets the LZ external dependencies.
```
Morpheus: We agree with this problem. We decided to change the permissions check for calling freeze/unfreeze functions to solve it. Now FreezableBeaconProxy is fully responsible for this. It dynamically checks the current owner of the contract when calling functions. We realize the possible problems if the owner() function is not present and we take this under our control. Because of this, the Factory will remain a proxy and the corresponding functions will be removed. BeaconProxy correctly checks that the protocol owner has not frozen the implementation. It is noteworthy that this change removes the ability to freeze the protocol deployment from the protocol deployer. Protocol deployers do no longer hold any privileges. Instead, protocol owners do.

## Recommendation
No data
