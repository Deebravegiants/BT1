# [M] `registerOrg` Function Vulnerable to DoS and Gas Griefing Attacks

## Summary
Severity: Medium
Chain: Smart contract
Component: Palmera
Published: 2024-06-24
Source: https://github.com/hats-finance/Palmera-0x5fee7541ddcd51ba9f4af606f87b2c42eea655be/issues/3
Type: hats-finding

## Details
**Github username:** @0xmahdirostami
**Twitter username:** 0xmahdirostami
**Submission hash (on-chain):** 0x3a209da07e47ea408d83f5ada006360c3e100671c7003cd5990f5fd8d705a2bf
**Severity:** medium

**Description:**
**Description**:
The `registerOrg` function in the contract can be exploited by an attacker to perform denial-of-service (DoS) attacks or gas griefing against other users. The function allows for the creation of organizations, but it doesn't adequately handle the scenario where an organization name is already registered. An attacker can front-run a legitimate user's transaction to create an organization with a desired name, causing the legitimate user's transaction to fail. This forces the user to attempt the process again.

**Impact**:
Denial of Service (DoS) and Gas Griefing

**Scenario**:
1. A user wants to create an organization with the name "organizationA".
2. A malicious user front-runs the transaction and creates an organization with the name "organizationA".
3. The user's transaction fails due to the name conflict.
4. The user has to go through the transaction process again, choosing a new name.
5. This process can be repeated by the attacker, continuously causing the user's transactions to fail.

**Proof of Concept (PoC)**:
The `registerOrg` function calls `_createOrgOrRoot`, which includes the following logic:
```solidity
function _createOrgOrRoot(
    string memory name,
    address caller,
    address newRootSafe
) private returns (uint256 safeId) {
    if (bytes(name).length == 0) {
        revert Errors.EmptyName();
    }
    bytes32 org = caller == newRootSafe
        ? bytes32(keccak256(abi.encodePacked(name)))
        : getOrgHashBySafe(caller);
    if (isOrgRegistered(org) && caller == newRootSafe) {
        revert Errors.OrgAlreadyRegistered(org);
    }
```
Due to the `isOrgRegistered` check, the function reverts if an organization with the same name is already registered.

_Trimmed to 38 lines — full report: https://github.com/hats-finance/Palmera-0x5fee7541ddcd51ba9f4af606f87b2c42eea655be/issues/3_
