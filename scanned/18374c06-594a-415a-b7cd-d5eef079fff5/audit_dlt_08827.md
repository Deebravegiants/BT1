# [?] fix(protocol): fix governor bravo vulnerability (#15947)

## Summary
Severity: Unknown
Chain: Taiko
Component: taikoxyz/taiko-mono
Published: 2024-02-20
Source: https://github.com/taikoxyz/taiko-mono/commit/a631be668b0bc6829643ccf02023ce13cbf19bc7
Type: security-commit

## Details
fix(protocol): fix governor bravo vulnerability (#15947)

Co-authored-by: Keszey Dániel <keszeyd@MacBook-Pro.local>

## Patch
### packages/protocol/contracts/L1/gov/TaikoGovernor.sol
```diff
@@ -26,14 +26,15 @@ import "../../common/OwnerUUPSUpgradable.sol";
 
 contract TaikoGovernor is
     OwnerUUPSUpgradable,
-    GovernorUpgradeable,
     GovernorCompatibilityBravoUpgradeable,
     GovernorVotesUpgradeable,
     GovernorVotesQuorumFractionUpgradeable,
     GovernorTimelockControlUpgradeable
 {
     uint256[50] private __gap;
 
+    error TG_INVALID_SIGNATURES_LENGTH();
+
     function init(
         IVotesUpgradeable _token,
         TimelockControllerUpgradeable _timelock
@@ -62,6 +63,31 @@ contract TaikoGovernor is
         return super.propose(targets, values, calldatas, description);
     }
 
+    /// @notice An overwrite of GovernorCompatibilityBravoUpgradeable's propose() as that one does
+    /// not checks the length of signatures equal to calldatas.
+    /// See vulnerability description here:
+    /// https://github.com/taikoxyz/taiko-mono/security/dependabot/114
+    /// See fix in OZ 4.8.3 here:
+    /// https://github.com/OpenZeppelin/openzeppelin-contracts/blob/0a25c1940ca220686588c4af3ec526f725fe2582/contracts/governance/compatibility/GovernorCompatibilityBravo.sol#L72
+    function propose(
+        address[] memory targets,
+        uint256[] memory values,
+        string[] memory signatures,
+        bytes[] memory calldatas,
+        string memory description
+    )
+        public
+        virtual
+        override(GovernorCompatibilityBravoUpgradeable)
+        returns (uint256)
+    {
+        if (signatures.length != calldatas.length) revert TG_INVALID_SIGNATURES_LENGTH();
+
+        return GovernorCompatibilityBravoUpgradeable.propose(
+            targets, values, signatures, calldatas, description
+        );
+    }
+
     function supportsInterface(bytes4 interfaceId)
         public
         view
```
