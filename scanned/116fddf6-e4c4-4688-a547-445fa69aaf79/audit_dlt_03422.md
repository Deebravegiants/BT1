# [M] Incorrect modifier condition

## Summary
Severity: Medium
Chain: Smart contract
Component: 2024-04-noya
Published: 2024-05-17
Source: https://github.com/code-423n4/2024-04-noya-findings/issues/1488
Type: code-finding

## Details
# Lines of code

https://github.com/code-423n4/2024-04-noya/blob/main/contracts/accountingManager/Registry.sol#L33-L35


# Vulnerability details

## Impact
The onlyVaultMaintainer modifier restricts access to certain functions, allowing only the vault maintainer or, in an emergency, someone with the EMERGENCY_ROLE to call them. However, due to a faulty condition, the transaction will fail if the caller is a vault maintainer without the EMERGENCY_ROLE, or if the caller has the EMERGENCY_ROLE but is not a vault maintainer.

To resolve this, the caller must be granted both the emergency role and vault maintainer status. This solution is flawed, as roles should be assigned selectively rather than universally. Each role needs to be designated to specific individuals appropriately.

## Proof of Concept
```sol
modifier onlyVaultMaintainer(uint256 _vaultId) {
    //@audit wrong validation
    if (msg.sender != vaults[_vaultId].maintainer || hasRole(EMERGENCY_ROLE, msg.sender) == false) {
        revert UnauthorizedAccess();
    }
    _;
}
```

## Tools Used
Manual Review

## Recommended Mitigation Steps
Change the `||` to `&&` to only abort if the caller is not the maintainer and the caller doesn't have `EMERGENCY_ROLE` role.
```diff
modifier onlyVaultMaintainer(uint256 _vaultId) {
-       if (msg.sender != vaults[_vaultId].maintainer || hasRole(EMERGENCY_ROLE, msg.sender) == false) {
+       if (msg.sender != vaults[_vaultId].maintainer && hasRole(EMERGENCY_ROLE, msg.sender) == false) {
        revert UnauthorizedAccess();
    }
    _;
}
```


_Trimmed to 38 lines — full report: https://github.com/code-423n4/2024-04-noya-findings/issues/1488_
