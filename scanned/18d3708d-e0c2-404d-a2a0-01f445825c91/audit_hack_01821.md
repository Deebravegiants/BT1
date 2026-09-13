# [M] Potentially inconsistent input validation

## Summary
Severity: Medium
Source: https://github.com/tintinweb/smart-contract-vulndb
Type: audit-issue

## Details
#### Description

There are some functions that might require additional input validation (similar to other functions):

#### Examples

- `Amp.transferWithData`: `require(_isOperator(msg.sender, _from), EC_58_INVALID_OPERATOR);` like in 

**code/amp-contracts/contracts/Amp.sol:L699**
```solidity
require(_isOperator(msg.sender, _from), EC_58_INVALID_OPERATOR);
```

- `Amp.authorizeOperatorByPartition`: `require(_operator != msg.sender);` like in 

**code/amp-contracts/contracts/Amp.sol:L789**
```solidity
require(_operator != msg.sender);
```

- `Amp.revokeOperatorByPartition`: `require(_operator != msg.sender);` like in 

**code/amp-contracts/contracts/Amp.sol:L800**
```solidity
require(_operator != msg.sender);
```

#### Recommendation

Consider adding additional input validation.
