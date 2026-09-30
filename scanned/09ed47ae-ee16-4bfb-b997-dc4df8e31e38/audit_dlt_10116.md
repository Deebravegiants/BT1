# [?] prevent index out of bounds exception

## Summary
Severity: Unknown
Chain: Neo
Component: neo-project/neo
Published: 2017-10-22
Source: https://github.com/neo-project/neo/commit/2be8715169d92247d4c0e054f0d83c47ab5674bb
Type: security-commit

## Details
prevent index out of bounds exception

## Patch
### neo/SmartContract/ContractParametersContext.cs
```diff
@@ -156,6 +156,12 @@ public bool AddSignature(Contract contract, ECPoint pubkey, byte[] signature)
                             throw new NotSupportedException();
                         else
                             index = i;
+
+                if(index == -1) {
+                    // unable to find ContractParameterType.Signature in contract.ParameterList 
+                    // return now to prevent array index out of bounds exception
+                    return false;
+                }
                 return Add(contract, index, signature);
             }
         }
```
