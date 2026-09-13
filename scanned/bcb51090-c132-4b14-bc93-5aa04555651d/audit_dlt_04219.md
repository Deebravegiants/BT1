# [M] Lack of two step admin ownership transfer for DODORouterProxy.sol

## Summary
Severity: Medium
Chain: Smart contract
Component: 2022-11-dodo
Published: 2022-11-15
Source: https://github.com/sherlock-audit/2022-11-dodo-judging/issues/23
Type: sherlock-finding

## Details
ctf_sec

medium

# Lack of two step admin ownership transfer for DODORouterProxy.sol

## Summary

Lack of two step admin ownership transfer for DODRouterProxy.sol

## Vulnerability Detail

The contract DODOApproveProxy implements a two-step ownership transfer because the contract inherits from  

```solidity
function transferOwnership(address newOwner) public onlyOwner {
    emit OwnershipTransferPrepared(_OWNER_, newOwner);
    _NEW_OWNER_ = newOwner;
}

function claimOwnership() public {
    require(msg.sender == _NEW_OWNER_, "INVALID_CLAIM");
    emit OwnershipTransferred(_OWNER_, _NEW_OWNER_);
    _OWNER_ = _NEW_OWNER_;
    _NEW_OWNER_ = address(0);
}
```

this is important because the claimOwnership function make the new admin has the intention and is capable of managing the contract.

The admin can control crucial contract function in DODORouterProxy.sol: the admin can whitelist swap target or approve target or adjust fees.

However, the DODORouterProxy.sol just inherits Openzepplin Ownable contract. Which does not two step admin ownership transfer implemented.

```solidity
contract DODORouteProxy is Ownable {
```

## Impact

Without the two-step admin transfer implemented, the newly assigned admin may be not able to manage the admin function, for example, if the admin is transferred to address(0) or a smart contract that cannot manage the contract, the project lose the access to admin function in DODORouterProxy.sol

## Code Snippet

https://github.com/sherlock-audit/2022-11-dodo/blob/main/contracts/SmartRoute/DODORouteProxy.sol#L35-L37

https://github.com/sherlock-audit/2022-11-dodo/blob/main/contracts/lib/InitializableOwnable.sol#L46-L57

## Tool used

Manual Review

## Recommendation

We recommend the project implement two step ownership transfer in DODORouterProxy.sol
