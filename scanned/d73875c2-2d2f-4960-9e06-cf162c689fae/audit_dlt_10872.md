# [?] fix: certora - reentrancy guards

## Summary
Severity: Unknown
Chain: Symbiotic
Component: symbioticfi/core
Published: 2024-08-28
Source: https://github.com/symbioticfi/core/commit/f6c67a7412e5f42775a6dafb9926749cb6e7826b
Type: security-commit

## Details
fix: certora - reentrancy guards

## Patch
### src/contracts/delegator/BaseDelegator.sol
```diff
@@ -15,8 +15,15 @@ import {Subnetwork} from "src/contracts/libraries/Subnetwork.sol";
 
 import {AccessControlUpgradeable} from "@openzeppelin/contracts-upgradeable/access/AccessControlUpgradeable.sol";
 import {Math} from "@openzeppelin/contracts/utils/math/Math.sol";
-
-contract BaseDelegator is Entity, StaticDelegateCallable, AccessControlUpgradeable, IBaseDelegator {
+import {ReentrancyGuardUpgradeable} from "@openzeppelin/contracts-upgradeable/utils/ReentrancyGuardUpgradeable.sol";
+
+contract BaseDelegator is
+    Entity,
+    StaticDelegateCallable,
+    AccessControlUpgradeable,
+    ReentrancyGuardUpgradeable,
+    IBaseDelegator
+{
     using Checkpoints for Checkpoints.Trace256;
     using Math for uint256;
     using Subnetwork for bytes32;
@@ -138,7 +145,7 @@ contract BaseDelegator is Entity, StaticDelegateCallable, AccessControlUpgradeab
     /**
      * @inheritdoc IBaseDelegator
      */
-    function setMaxNetworkLimit(uint96 identifier, uint256 amount) external {
+    function setMaxNetworkLimit(uint96 identifier, uint256 amount) external nonReentrant {
         if (!IRegistry(NETWORK_REGISTRY).isEntity(msg.sender)) {
             revert NotNetwork();
         }
@@ -158,7 +165,7 @@ contract BaseDelegator is Entity, StaticDelegateCallable, AccessControlUpgradeab
     /**
      * @inheritdoc IBaseDelegator
      */
-    function setHook(address hook_) external onlyRole(HOOK_SET_ROLE) {
+    function setHook(address hook_) external nonReentrant onlyRole(HOOK_SET_ROLE) {
         hook = hook_;
 
         emit SetHook(hook_);
@@ -173,7 +180,7 @@ contract BaseDelegator is Entity, StaticDelegateCallable, AccessControlUpgradeab
         uint256 slashedAmount,
         uint48 captureTimestamp,
         bytes memory data
-    ) external {
+    ) external nonReentrant {
         if (IVault(vault).slasher() != msg.sender) {
             revert NotSlasher();
         }
@@ -203,6 +210,8 @@ contract BaseDelegator is Entity, StaticDelegateCallable, AccessControlUpgradeab
             revert NotVault();
         }
 
+        __ReentrancyGuard_init();
+
         vault = vault_;
 
         IBaseDelegator.BaseParams memory baseParams = __initialize(vault_, data_);
```

### src/contracts/slasher/BaseSlasher.sol
```diff
@@ -14,9 +14,10 @@ import {Checkpoints} from "src/contracts/libraries/Checkpoints.sol";
 import {Subnetwork} from "src/contracts/libraries/Subnetwork.sol";
 
 import {Math} from "@openzeppelin/contracts/utils/math/Math.sol";
+import {ReentrancyGuardUpgradeable} from "@openzeppelin/contracts-upgradeable/utils/ReentrancyGuardUpgradeable.sol";
 import {Time} from "@openzeppelin/contracts/utils/types/Time.sol";
 
-abstract contract BaseSlasher is Entity, StaticDelegateCallable, IBaseSlasher {
+abstract contract BaseSlasher is Entity, StaticDelegateCallable, ReentrancyGuardUpgradeable, IBaseSlasher {
     using Checkpoints for Checkpoints.Trace256;
     using Subnetwork for bytes32;
 
@@ -129,6 +130,8 @@ abstract contract BaseSlasher is Entity, StaticDelegateCallable, IBaseSlasher {
             revert NotVault();
         }
 
+        __ReentrancyGuard_init();
+
         vault = vault_;
 
         __initialize(vault_, data_);
```

### src/contracts/slasher/Slasher.sol
```diff
@@ -27,7 +27,7 @@ contract Slasher is BaseSlasher, ISlasher {
         uint256 amount,
         uint48 captureTimestamp,
         bytes calldata hints
-    ) external onlyNetworkMiddleware(subnetwork) returns (uint256 slashedAmount) {
+    ) external nonReentrant onlyNetworkMiddleware(subnetwork) returns (uint256 slashedAmount) {
         SlashHints memory slashHints;
         if (hints.length > 0) {
             slashHints = abi.decode(hints, (SlashHints));
```

### src/contracts/slasher/VetoSlasher.sol
```diff
@@ -83,7 +83,7 @@ contract VetoSlasher is BaseSlasher, IVetoSlasher {
         uint256 amount,
         uint48 captureTimestamp,
         bytes calldata hints
-    ) external onlyNetworkMiddleware(subnetwork) returns (uint256 slashIndex) {
+    ) external nonReentrant onlyNetworkMiddleware(subnetwork) returns (uint256 slashIndex) {
         RequestSlashHints memory requestSlashHints;
         if (hints.length > 0) {
             requestSlashHints = abi.decode(hints, (RequestSlashHints));
@@ -125,7 +125,10 @@ contract VetoSlasher is BaseSlasher, IVetoSlasher {
     /**
      * @inheritdoc IVetoSlasher
      */
-    function executeSlash(uint256 slashIndex, bytes calldata hints) external returns (uint256 slashedAmount) {
+    function executeSlash(
+        uint256 slashIndex,
+        bytes calldata hints
+    ) external nonReentrant returns (uint256 slashedAmount) {
         ExecuteSlashHints memory executeSlashHints;
         if (hints.length > 0) {
             executeSlashHints = abi.decode(hints, (ExecuteSlashHints));
@@ -190,7 +193,7 @@ contract VetoSlasher is BaseSlasher, IVetoSlasher {
     /**
      * @inheritdoc IVetoSlasher
      */
-    function vetoSlash(uint256 slashIndex, bytes calldata hints) external {
+    function vetoSlash(uint256 slashIndex, bytes calldata hints) external nonReentrant {
         VetoSlashHints memory vetoSlashHints;
         if (hints.length > 0) {
             vetoSlashHints = abi.decode(hints, (VetoSlashHints));
@@ -228,7 +231,7 @@ contract VetoSlasher is BaseSlasher, IVetoSlasher {
         emit VetoSlash(slashIndex, msg.sender);
     }
 
-    function setResolver(uint96 identifier, address resolver_, bytes calldata hints) external {
+    function setResolver(uint96 identifier, address resolver_, bytes calldata hints) external nonReentrant {
         SetResolverHints memory setResolverHints;
         if (hints.length > 0) {
             setResolverHints = abi.decode(hints, (SetResolverHints));
```

### src/contracts/vault/Vault.sol
```diff
@@ -192,7 +192,7 @@ contract Vault is VaultStorage, MigratableEntity, AccessControlUpgradeable, Reen
     /**
      * @inheritdoc IVault
      */
-    function onSlash(uint256 slashedAmount, uint48 captureTimestamp) external {
+    function onSlash(uint256 slashedAmount, uint48 captureTimestamp) external nonReentrant {
         if (msg.sender != slasher) {
             revert NotSlasher();
         }
@@ -245,7 +245,7 @@ contract Vault is VaultStorage, MigratableEntity, AccessControlUpgradeable, Reen
     /**
      * @inheritdoc IVault
      */
-    function setDepositWhitelist(bool status) external onlyRole(DEPOSIT_WHITELIST_SET_ROLE) {
+    function setDepositWhitelist(bool status) external nonReentrant onlyRole(DEPOSIT_WHITELIST_SET_ROLE) {
         if (depositWhitelist == status) {
             revert AlreadySet();
         }
@@ -258,7 +258,10 @@ contract Vault is VaultStorage, MigratableEntity, AccessControlUpgradeable, Reen
     /**
      * @inheritdoc IVault
      */
-    function setDepositorWhitelistStatus(address account, bool status) external onlyRole(DEPOSITOR_WHITELIST_ROLE) {
+    function setDepositorWhitelistStatus(
+        address account,
+        bool status
+    ) external nonReentrant onlyRole(DEPOSITOR_WHITELIST_ROLE) {
         if (account == address(0)) {
             revert InvalidAccount();
         }
@@ -279,7 +282,7 @@ contract Vault is VaultStorage, MigratableEntity, AccessControlUpgradeable, Reen
     /**
      * @inheritdoc IVault
      */
-    function setIsDepositLimit(bool status) external onlyRole(IS_DEPOSIT_LIMIT_SET_ROLE) {
+    function setIsDepositLimit(bool status) external nonReentrant onlyRole(IS_DEPOSIT_LIMIT_SET_ROLE) {
         if (isDepositLimit == status) {
             revert AlreadySet();
         }
@@ -292,7 +295,7 @@ contract Vault is VaultStorage, MigratableEntity, AccessControlUpgradeable, Reen
     /**
      * @inheritdoc IVault
      */
-    function setDepositLimit(uint256 limit) external onlyRole(DEPOSIT_LIMIT_SET_ROLE) {
+    function setDepositLimit(uint256 limit) external nonReentrant onlyRole(DEPOSIT_LIMIT_SET_ROLE) {
         if (limit != 0 && !isDepositLimit) {
             revert NoDepositLimit();
         }
```
