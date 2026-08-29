# [M] Once an address is made an admin via updateAdmin, there is no way to revoke that privilege

## Summary
Severity: Medium
Chain: Smart contract
Component: ether-fi
Published: 2023-11-06
Source: https://github.com/hats-finance/ether-fi-0x36c3b77853dec9c4a237a692623293223d4b9bc4/issues/4
Type: hats-finding

## Details
**Github username:** --
**Submission hash (on-chain):** 0x26361656404c6c1b17e5a2cee60e3e4f891ec6caa7061603989d60fbd69dbffa
**Severity:** medium

**Description:**
**Description**\
The admins mapping is defined as:
mapping(address => bool) public admins;
This mapping stores admin status – true means the address is an admin, false means they are not.
The updateAdmin function only allows setting the value to true:
function updateAdmin(address _address, bool _isAdmin) external onlyOwner {
  admins[_address] = _isAdmin; 
}
There is no functionality to ever set an address back to false once made an admin.
This means any address that is ever set as an admin via updateAdmin will remain an admin forever. There is no way to revoke their privileges.

**Attack Scenario**\
Once an address is made an admin via updateAdmin, there is no way to revoke that privilege

**Attachments**
https://github.com/GadzeFinance/dappContracts/blob/68bf2597086d9aa39968c504f04cf34aa0f864c0/src/EtherFiNodesManager.sol#L415-L417


**Recommendation**\

Add this to the code:

function revokeAdmin(address _address) external onlyOwner {
  admins[_address] = false;
}
