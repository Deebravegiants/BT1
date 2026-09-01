# [M] Centralization risk: admin can with rug the project by removing asset and price manipulation on oracle.

## Summary
Severity: Medium
Chain: Smart contract
Component: 2022-11-paraspace
Published: 2022-12-09
Source: https://github.com/code-423n4/2022-11-paraspace-findings/issues/437
Type: code-finding

## Details
# Lines of code

https://github.com/code-423n4/2022-11-paraspace/blob/c6820a279c64a299a783955749fdc977de8f0449/paraspace-core/contracts/misc/ParaSpaceOracle.sol#L21
https://github.com/code-423n4/2022-11-paraspace/blob/c6820a279c64a299a783955749fdc977de8f0449/paraspace-core/contracts/protocol/configuration/ACLManager.sol#L14
https://github.com/code-423n4/2022-11-paraspace/blob/c6820a279c64a299a783955749fdc977de8f0449/paraspace-core/contracts/protocol/tokenization/NToken.sol#L29


# Vulnerability details

## Impact

admin can with rug the project by removing asset and price manipulation on oracle.

## Proof of Concept

As we see what happens in ankr when the admin is compromised, the centralization risk should not be taken lightly.

https://rekt.news/ankr-helio-rekt/

If the admin is compromised in paraspace, the admin can set the reward controller to invalid address, and can call resuceERC20 and rescue721 token from NToken to remove asset with no restriction or add or disable address in ACL manager directly.

```solidity
28 results - 11 files

paraspace-core\contracts\protocol\configuration\PriceOracleSentinel.sol:
  20       **/
  21:     modifier onlyPoolAdmin() {
  22          IACLManager aclManager = IACLManager(

  92          external
  93:         onlyPoolAdmin
  94      {

paraspace-core\contracts\protocol\pool\PoolConfigurator.sol:
   31       **/
   32:     modifier onlyPoolAdmin() {
   33:         _onlyPoolAdmin();
   34          _;
```

_Trimmed to 38 lines — full report: https://github.com/code-423n4/2022-11-paraspace-findings/issues/437_
