# [H] AccessControlManager is in charge of managing roles and permissions for accounts to determine what users can call on which contracts

## Summary
Severity: High
Contest weight: 0.0000
Dataset id: 23374
Source: https://huggingface.co/datasets/Zaevlad/audit-findings-dataset
Type: audit-finding

## Details
AccessControlManager is in charge of managing roles and permissions for accounts to determine what users can call on which contracts.  
Permissions are granted at the selector level, and is possible to grant permissions to only one contract at a time, or authorize an account to call the same selector on any contract.  
There is an edge case when permitting an account to call the fallback() function whose selector is bytes4(0) on any account (address(0)).  

The combination of those two inputs results in calculating the role as bytes(0), which is the exact value assigned for the DEFAULT_ADMIN_ROLE.  

```solidity
function grantCall(address contractAddress, bytes4 sel, address accountToPermit) public {
    //@audit-issue => The calculated role for `address(0)` and `bytes4(0)` is bytes32(0)`
    bytes32 role = roleFor(contractAddress, sel);
    //@audit-issue => Granting bytes32(0) to the account results in granting the DEFAULT_ADMIN_ROLE
    grantRole(role, accountToPermit);
    emit PermissionGranted(accountToPermit, contractAddress, sel);
}
function roleFor(address contractAddress, bytes4 sel) internal pure returns (bytes32 role) {
    //@audit-issue => The calculated role for `address(0)` and `bytes4(0)` is bytes32(0)`
    role = (bytes32(uint256(uint160(contractAddress))) << 96) | bytes32(uint256(uint32(sel)));
}
```

Impact: Users can be mistakenly granted the DEFAULT_ADMIN_ROLE, which they can then use to authorize other users to call restricted functions.

## Proof of Concept
Add the next PoC to CDO.t.sol test file:

```solidity
function test_grantsDefaultAdminByMisstake() public {
    bytes32 DEFAULT_ADMIN_ROLE = acm.DEFAULT_ADMIN_ROLE();
    address contractAddress = address(0);
    bytes4 selector = bytes4(0);
    address alice = makeAddr("Alice");
    assertFalse(acm.hasRole(DEFAULT_ADMIN_ROLE, alice));
    //@audit-issue => Granting permission to alice to call fallback function on any contract results
    on granting Alice the DEFAULT_ADMIN_ROLE,!
    24
    acm.grantCall(contractAddress, selector, alice);
    assertTrue(acm.hasRole(DEFAULT_ADMIN_ROLE, alice));
    address contractA = makeAddr("contractA");
    address bob = makeAddr("bob");
    bytes4 withdrawSelector = bytes4(keccak256(bytes("withdraw(address,uint256)")));
    assertFalse(acm.hasPermission(bob, contractA, withdrawSelector));
    //@audit-info => Alice w/ DEFAULT_ADMIN can grant permissions to other accounts
    vm.startPrank(alice);
    acm.grantCall(contractA, withdrawSelector, bob);
    assertTrue(acm.hasPermission(bob, contractA, withdrawSelector));
}
```

## Recommendation
Validate that the computed role is not the DEFAULT_ADMIN_ROLE; otherwise, revert the tx.

```solidity
function grantCall(address contractAddress, bytes4 sel, address accountToPermit) public {
    bytes32 role = roleFor(contractAddress, sel);
    + require(role != DEFAULT_ADMIN_ROLE, "Granting DEFAULT_ADMIN_ROLE");
    grantRole(role, accountToPermit);
    emit PermissionGranted(accountToPermit, contractAddress, sel);
}
```
