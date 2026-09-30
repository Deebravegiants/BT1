# [?] Fix crash when comparing ContractPermissionDescriptor (#3396)

## Summary
Severity: Unknown
Chain: Neo
Component: neo-project/neo
Published: 2024-07-05
Source: https://github.com/neo-project/neo/commit/2c2082084e705d148221281d5dbc65ef72f426e5
Type: security-commit

## Details
Fix crash when comparing ContractPermissionDescriptor (#3396)

* Update ContractPermissionDescriptor.cs

* Add UT

---------

Co-authored-by: Fernando Diaz Toledano <shargon@gmail.com>
Co-authored-by: Christopher Schuchardt <cschuchardt88@gmail.com>
Co-authored-by: NGD Admin <154295625+NGDAdmin@users.noreply.github.com>

## Patch
### src/Neo/SmartContract/Manifest/ContractPermissionDescriptor.cs
```diff
@@ -114,7 +114,8 @@ public bool Equals(ContractPermissionDescriptor other)
             if (this == other) return true;
             if (IsWildcard == other.IsWildcard) return true;
             if (IsHash) return Hash.Equals(other.Hash);
-            else return Group.Equals(other.Group);
+            if (IsGroup) return Group.Equals(other.Group);
+            return false;
         }
 
         public override int GetHashCode()
```

### tests/Neo.UnitTests/SmartContract/Manifest/UT_ContractPermissionDescriptor.cs
```diff
@@ -11,6 +11,7 @@
 
 using Microsoft.VisualStudio.TestTools.UnitTesting;
 using Neo.SmartContract.Manifest;
+using Neo.SmartContract.Native;
 using Neo.Wallets;
 using System.Security.Cryptography;
 
@@ -44,5 +45,18 @@ public void TestFromAndToJson()
             Assert.AreEqual(null, result.Hash);
             Assert.AreEqual(result.Group, result.Group);
         }
+
+        [TestMethod]
+        public void TestEquals()
+        {
+            var descriptor1 = ContractPermissionDescriptor.CreateWildcard();
+            var descriptor2 = ContractPermissionDescriptor.Create(LedgerContract.NEO.Hash);
+
+            Assert.AreNotEqual(descriptor1, descriptor2);
+
+            var descriptor3 = ContractPermissionDescriptor.Create(LedgerContract.NEO.Hash);
+
+            Assert.AreEqual(descriptor2, descriptor3);
+        }
     }
 }
```
