# [?] fix(protocol): fix bond manager vulnerability (#20484)

## Summary
Severity: Unknown
Chain: Taiko
Component: taikoxyz/taiko-mono
Published: 2025-10-21
Source: https://github.com/taikoxyz/taiko-mono/commit/4f67af17ee4792b8a444650a143afd103470bc1a
Type: security-commit

## Details
fix(protocol): fix bond manager vulnerability (#20484)

Co-authored-by: Gustavo Gonzalez <gustavo@taiko.xyz>

## Patch
### packages/protocol/contracts/layer2/core/BondManager.sol
```diff
@@ -201,9 +201,9 @@ contract BondManager is EssentialContract, IBondManager {
     /// @param _to The recipient address
     /// @param _amount The amount to withdraw
     function _withdraw(address _from, address _to, uint256 _amount) internal {
-        _debitBond(_from, _amount);
-        bondToken.safeTransfer(_to, _amount);
-        emit BondWithdrawn(_from, _amount);
+        uint256 debited = _debitBond(_from, _amount);
+        bondToken.safeTransfer(_to, debited);
+        emit BondWithdrawn(_from, debited);
     }
 
     /// @dev Internal implementation for getting the bond balance
```
