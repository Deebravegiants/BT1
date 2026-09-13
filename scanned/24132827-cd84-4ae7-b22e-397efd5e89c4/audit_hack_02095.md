# [M] 6.5 Role Switch Needed

## Summary
Severity: Medium
Source: https://github.com/tintinweb/smart-contract-vulndb
Type: audit-issue

## Details
Design Medium Version 1 Acknowledged

The TokenMinter contract calls permissioned token contract functions. These are mint,
setBridgeContract, transferOwnership. To successfully call these functions, the TokenMinter
contract needs to be the owner of the ERC677MultiBridgeToken contract.

Regarding the setBridgeContract we have opened a separate issue because this call will always fail.
But the ERC677MultiBridgeToken contract also implements other functions that are permissioned to
be called only by the owner. Given the TokenMinter contract is the owner these functions could not be
called. These functions are: addBridge, removeBridge, setBlockRewardContract,
setStakingcontract.

To call this functions, the ownership needs to be transferred from the minter contract to an other contract
and then back. This seems undesirable.

Acknowledged:

POA Network explains that the TokenMinter contract is used as an intermediate owner contract for the
PermittableToken contract wich represents the STAKE token. To clarify this, comments where added to
the TokenMinter contract.
