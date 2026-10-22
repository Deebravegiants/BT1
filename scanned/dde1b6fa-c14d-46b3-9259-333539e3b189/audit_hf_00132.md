# [H] auth collision possible

## Summary
Severity: High
Contest weight: 0.7824
Dataset id: 419
Source: https://huggingface.co/datasets/Zaevlad/audit-findings-dataset
Type: audit-finding

## Details
The auth mechanism of `AccessControl.sol` uses function selectors `(msg.sig)` as a `(unique)` role definition. Also the `_moduleCall` allows the code to be extended.

Suppose an attacker wants to add the innocent-looking function ”`left_branch_block(uint32)` “in a new module. Suppose this module is added via `_moduleCall`, and the attacker gets authorization for the innocent function.

This function happens to have a signature of 0x00000000, which is equal to the root authorization. In this way, the attacker could get authorization for the entire project.

Note: it’s pretty straightforward to generate function names for any signature value; you can just brute force it because it’s only 4 bytes.

Recommend not allowing third parties to define or suggest new modules and double-checking the function signatures of new functions of a new module for collisions.

The execution of any `auth` function will only happen after a governance process or by a contract that has gone through a thorough review and governance process.

We are aware that new modules can have complete control of the Ladle, and for that reason, the addition of new modules would be subject to the highest level of scrutiny. Checking for signature collisions is a good item to add to that process.

In addition to that, I would implement two changes in `AccessControl.sol` so that giving ROOT access is explicit.

```solidity
function grantRole(bytes4 role, address account) external virtual admin(role) {
    require(role != ROOT, "Not ROOT role");
    _grantRole(role, account);
}
```

```solidity
function grantRoot(address account) external virtual admin(ROOT) {
    _grantRole(ROOT, account);
}
```

However, given that this could be exploited only through a malicious governance exploit, I would reduce the risk to “Low.”

After further thinking, instead of preventing auth collisions in the smart contracts, we will add CI checks for this specific issue instead.

## Recommendation
No recommendation
