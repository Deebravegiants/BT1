# [M] Potentially missing nonce check

## Summary
Severity: Medium
Source: https://github.com/tintinweb/smart-contract-vulndb
Type: audit-issue

## Details
#### Description

When executing withdrawals in the collateral manager the per-address withdrawal nonce is simply updated without checking that the new nonce is one greater than the previous one (see Examples). It seems like without such a check it might be  easy to make mistakes and causing issues with ordering of withdrawals.

#### Examples


**code/flexa-collateral-manager/contracts/FlexaCollateralManager.sol:L663-L664**
```solidity
addressToWithdrawalNonce[_partition][supplier] = withdrawalRootNonce;

```


**code/flexa-collateral-manager/contracts/FlexaCollateralManager.sol:L845-L846**
```solidity
addressToWithdrawalNonce[_partition][supplier] = maxWithdrawalRootNonce;

```


**code/flexa-collateral-manager/contracts/FlexaCollateralManager.sol:L1155-L1156**
```solidity
maxWithdrawalRootNonce = _nonce;

```

#### Recommendation

Consider adding more validation and sanity checks for nonces on per-address withdrawals.
