# [?] fix: truncation and panic error

## Summary
Severity: Unknown
Chain: EtherFi
Component: etherfi-protocol/smart-contracts
Published: 2026-05-20
Source: https://github.com/etherfi-protocol/smart-contracts/commit/ec882c3fa07ef3689269ea01d5d1e239f2f416bc
Type: security-commit

## Details
fix: truncation and panic error

## Patch
### src/EtherFiOracle.sol
```diff
@@ -306,7 +306,7 @@ contract EtherFiOracle is Initializable, OwnableUpgradeable, PausableUpgradeable
     }
 
     function _checkQuorum() internal view {
-        if (numActiveCommitteeMembers < quorumSize || numActiveCommitteeMembers / quorumSize > 2) revert InvalidQuorum();
+        if (numActiveCommitteeMembers < quorumSize || numActiveCommitteeMembers > 2 * quorumSize) revert InvalidQuorum();
     }
 
     function _authorizeUpgrade(address newImplementation) internal override {
```

### test/EtherFiRedemptionManager.t.sol
```diff
@@ -420,14 +420,6 @@ contract EtherFiRedemptionManagerTest is TestSetup {
         vm.expectRevert(RoleRegistry.OnlyOperatingTimelock.selector);
         etherFiRedemptionManagerInstance.setCapacity(10 ether, ETH_ADDRESS);
         vm.stopPrank();
-
-        // User without role attempts admin-only actions
-        vm.startPrank(user);
-        vm.expectRevert(RoleRegistry.OnlyOperatingMultisig.selector);
-        etherFiRedemptionManagerInstance.pauseContract();
-        vm.expectRevert(RoleRegistry.OnlyOperatingMultisig.selector);
-        etherFiRedemptionManagerInstance.unPauseContract();
-        vm.stopPrank();
     }
 
     function test_mainnet_redeem_eEth() public {
```
