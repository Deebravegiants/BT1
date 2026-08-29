# [M] initialize() function can be called by anybody

## Summary
Severity: Medium
Chain: Smart contract
Component: 2022-11-telcoin
Published: 2022-11-22
Source: https://github.com/sherlock-audit/2022-11-telcoin-judging/issues/63
Type: sherlock-finding

## Details
0xSmartContract

medium

# initialize() function can be called by anybody

## Summary
`initialize()` function can be called anybody when the contract is not initialized.


## Vulnerability Detail
More importantly, if someone else runs this function, they will have full authority because of the `_setupRole(DEFAULT_ADMIN_ROLE, msg.sender)` function.

Also, there is no 0 address check in the address arguments of the initialize() function, which must be defined.

## Impact

## Code Snippet
[StakingModule.sol#L60-L70](https://github.com/sherlock-audit/2022-11-telcoin/blob/main/contracts/StakingModule.sol#L60-L70)

Here is a definition of `initialize()` function.

```solidity
contracts/StakingModule.sol:
  78     
  79:     function initialize(address _telAddress) public payable initializer {
  80:         tel = _telAddress;
  81: 
  82:         // initialize OZ stuff
  83:         ReentrancyGuardUpgradeable.__ReentrancyGuard_init_unchained();
  84:         AccessControlEnumerableUpgradeable.__AccessControlEnumerable_init_unchained();
  85:         PausableUpgradeable.__Pausable_init_unchained();
  86: 
  87:         // set deployer as ADMIN
  88:         _setupRole(DEFAULT_ADMIN_ROLE, msg.sender);
  89:     }
```


_Trimmed to 38 lines — full report: https://github.com/sherlock-audit/2022-11-telcoin-judging/issues/63_
