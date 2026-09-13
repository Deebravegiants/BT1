# [M] A single point of failure is not acceptable for this project

## Summary
Severity: Medium
Chain: Smart contract
Component: 2022-11-telcoin
Published: 2022-11-22
Source: https://github.com/sherlock-audit/2022-11-telcoin-judging/issues/62
Type: sherlock-finding

## Details
0xSmartContract

medium

# A single point of failure is not acceptable for this project

## Summary

In the constructor of the `StakingModule` contract msg.sender is defined as `DEFAULT_ADMIN_ROLE` and `admin` is a critical address and this address is very important for the project
However, there is no timelock for this address to use its privileges and it is not managed with multisig (There is no information in the Document or NatSpec comments)

For these reasons ; Project has "Single Point of Failure"


## Vulnerability Detail
admin is responsible for defining the following roles, so its management is important;
SLASHER_ROLE
PLUGIN_EDITOR_ROLE
PAUSER_ROLE
RECOVERY_ROLE

## Impact
Even if protocol admins is not malicious there is still a chance for Owner keys to be stolen. In such a case, the attacker can cause serious damage to the project due to important functions. In such a case, users who have invested in project will suffer high financial losses.

This increases the risk of `A single point of failure`


Similar vulnerability;
Private keys stolen:

Hackers have stolen cryptocurrency worth around €552 million from a blockchain project linked to the popular online game Axie Infinity, in one of the largest cryptocurrency heists on record. Security issue : PrivateKey of the project officer was stolen:
https://www.euronews.com/next/2022/03/30/blockchain-network-ronin-hit-by-552-million-crypto-heist


## Code Snippet

[StakingModule.sol#L69](https://github.com/sherlock-audit/2022-11-telcoin/blob/main/contracts/StakingModule.sol#L69)
defined to admin in initialize function;

```solidity
contracts/StakingModule.sol:    
  79:     function initialize(address _telAddress) public payable initializer {
 
  87:         // set deployer as ADMIN
  88:         _setupRole(DEFAULT_ADMIN_ROLE, msg.sender);
  89:     }
```
## Tool used

Manual Review

## Recommendation

Add a time lock to  critical functions. Admin-role only functions that change critical parameters should emit events and have timelocks. 

Events allow capturing the changed parameters so that off-chain tools/interfaces can register such changes with timelocks that allow users to evaluate them and consider if they would like to engage/exit based on how they perceive the changes as affecting the trustworthiness of the protocol or profitability of the implemented financial services.

Allow only multi-signature wallets to call the function to reduce the likelihood of an attack.

https://twitter.com/danielvf/status/1572963475101556738?s=20&t=V1kvzfJlsx-D2hfnG0OmuQ

Also detail them in documentation and NatSpec comments
