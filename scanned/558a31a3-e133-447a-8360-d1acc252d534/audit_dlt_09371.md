# [?] Expose Vault's reentrancy guard (#281)

## Summary
Severity: Unknown
Chain: Balancer
Component: balancer/balancer-v3-monorepo
Published: 2024-02-07
Source: https://github.com/balancer/balancer-v3-monorepo/commit/1da6dde3212b7fb172c2c2e87ac926dda5afc3c9
Type: security-commit

## Details
Expose Vault's reentrancy guard (#281)

## Patch
### pkg/interfaces/contracts/test/IVaultMainMock.sol
```diff
@@ -50,4 +50,8 @@ interface IVaultMainMock {
         uint256 tokenIndex,
         uint256 yieldFeePercentage
     ) external pure returns (uint256);
+
+    function guardedCheckEntered() external;
+
+    function unguardedCheckNotEntered() external view;
 }
```

### pkg/vault/contracts/VaultCommon.sol
```diff
@@ -54,6 +54,14 @@ abstract contract VaultCommon is IVaultEvents, IVaultErrors, VaultStorage, Reent
         _;
     }
 
+    /**
+     * @notice Expose the state of the Vault's reentrancy guard.
+     * @return True if the Vault is currently executing a nonReentrant function
+     */
+    function reentrancyGuardEntered() public view returns (bool) {
+        return _reentrancyGuardEntered();
+    }
+
     /**
      * @notice Records the `debt` for a given handler and token.
      * @param token   The ERC20 token for which the `debt` will be accounted.
```

### pkg/vault/contracts/test/VaultMock.sol
```diff
@@ -154,4 +154,12 @@ contract VaultMock is IVaultMainMock, Vault {
             (, lastLiveBalances[i]) = poolTokenBalances.unchecked_at(i);
         }
     }
+
+    function guardedCheckEntered() external nonReentrant {
+        require(reentrancyGuardEntered());
+    }
+
+    function unguardedCheckNotEntered() external view {
+        require(!reentrancyGuardEntered());
+    }
 }
```

### pkg/vault/test/Vault.test.ts
```diff
@@ -547,4 +547,14 @@ describe('Vault', function () {
       });
     });
   });
+
+  describe('reentrancy guard state', () => {
+    it('reentrancy guard should be false when not in Vault context', async () => {
+      expect(await vault.unguardedCheckNotEntered()).to.not.be.reverted;
+    });
+
+    it('reentrancy guard should be true when in Vault context', async () => {
+      expect(await vault.guardedCheckEntered()).to.not.be.reverted;
+    });
+  });
 });
```
