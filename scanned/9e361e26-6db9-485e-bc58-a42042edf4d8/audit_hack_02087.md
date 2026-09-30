# [M] 7.7 feeRecepient of AddressRegistry

## Summary
Severity: Medium
Source: https://github.com/tintinweb/smart-contract-vulndb
Type: audit-issue

## Details
Correctness Medium Version 1 Code Corrected

In the last paragraph of section Architectural decisions of the specification document it's
mentioned that the feeRecipient is part of the off-chain registry (the struct AddressRegistry
passed as function parameter):

```
A caveat that has been raised is that using an off-chain registry managed by the frontend opens for
other frontends using our smart contract while passing their own fee wallet address in the params.
```
This struct features a field feeRecepient:

```
struct AddressRegistry {
address jug;
address manager;
address multiplyProxyActions;
address aaveLendingPoolProvider;
address feeRecepient;
address exchange;
}
```
However in the smart contracts reviewed, this field is never read. The exchange contract uses a
feeBeneficiary variable set in the constructor.

Code corrected:

feeRecepient was removed from the struct.
