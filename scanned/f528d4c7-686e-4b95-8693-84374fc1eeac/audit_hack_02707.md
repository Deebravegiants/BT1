# [M] VaultDiamond.sol, Auction.sol and Queue.sol can transfer ownership to zero address

## Summary
Severity: Medium
Reporter: ctf_sec
Source: https://github.com/solidstate-network/solidstate-solidity/blob/9a99628af2daacc26929f84ff29a6a30ae365d8d/contracts/proxy/diamond/SolidStateDiamond.sol#L101
Type: audit-issue

## Details
# VaultDiamond.sol, Auction.sol and Queue.sol can transfer ownership to zero address

## Summary

VaultDiamond.sol, Auction.sol and Queue.sol can transfer ownership to zero address

## Vulnerability Detail

VaultDiamond.sol implements novel EIP-2535 

https://eips.ethereum.org/EIPS/eip-2535

the admin can upgrade the smart contract by adding or removing function signature and can make the smart contract immutable.

however, the VaultDiamond inherits from SolidStateDiamond

```solidity
contract VaultDiamond is SolidStateDiamond
```

and insitde SolidStateDiamond, below function does not check if the account address is 0 when transferring ownership.

https://github.com/solidstate-network/solidstate-solidity/blob/9a99628af2daacc26929f84ff29a6a30ae365d8d/contracts/proxy/diamond/SolidStateDiamond.sol#L101

```solidity
    function _transferOwnership(address account)
        internal
        virtual
        override(OwnableInternal, SafeOwnable)
    {
        super._transferOwnership(account);
    }
``` 

and function _transferOwnership comes from 

https://github.com/solidstate-network/solidstate-solidity/blob/9a99628af2daacc26929f84ff29a6a30ae365d8d/contracts/access/ownable/OwnableInternal.sol#L45

```solidity
    function _transferOwnership(address account) internal virtual {
        OwnableStorage.layout().setOwner(account);
        emit OwnershipTransferred(msg.sender, account);
    }
```

SolidStateDiamond inherit from OwnableInternal,

AuctionInternal and QueueInternal also inherits from OwnableInternal

https://github.com/sherlock-audit/2022-09-knox/blob/main/knox-contracts/contracts/queue/QueueInternal.sol#L23-L28

https://github.com/sherlock-audit/2022-09-knox/blob/main/knox-contracts/contracts/auction/AuctionInternal.sol#L24

so Auction and Queue and Vault contract's ownership can also be transferred to zero address.

## Impact

If admin address is transferred to 0

the project loss all the benefits all using diamond standard.

the contract is not upgradeable any more. If the protocol may force to deploy everything again if the protocol want to make upgrade, which is error prone due to complicated configuration. 

the project will loss all the governance and admin function in Auction and Queue smart contract to adjust the project setting.

## Code Snippet

## Tool used

Manual Review

## Recommendation

We recommand the project overwrite the _transferOwnership function add check to make sure address(0) cannot become the admin
of the diamond contract, Auction and Queue contract.

```solidity
 require(account != address(0), "invalid owner")
```

Special notes about EIP-2535

Also the this EIP-2535 diamond is very new and may have undiscovered bug because the EIP protocol itself is not finalized yet.

We recommend the project use such a new standard with caution.

https://eips.ethereum.org/EIPS/eip-2535


![image](https://user-images.githubusercontent.com/114844362/193680112-3f5259e6-dbac-44d8-9786-8929bfabe978.png)
