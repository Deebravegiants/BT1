# [M] 5.2.7 Unvalidateddestinationaddress in Gravity faucet

## Summary
Severity: Medium
Source: https://github.com/tintinweb/smart-contract-vulndb
Type: audit-issue

## Details
**Severity:** Medium Risk
**Context:** GravityFacet.sol#L
**Description:** In the Gravity faucet, there is an issue related to the validation of the _gravity-
Data.destinationAddressaddress. The code does not validate if the provided destination address is in the valid
bech32format.
This can potentially cause issues when sending tokens to the destination address. If the provided address is not
in thebech32format, the tokens can be locked. Also, it can lead to confusion for the end-users as they might enter
an invalid address and lose their tokens without any warning or error message.
**Recommendation:** To mitigate this issue, it is recommended to add a validation check for the_gravity-
Data.destinationAddressaddress. The validation should ensure that the provided address is in the validbech
format. This will help prevent the loss of tokens and provide better error handling for the end users.
Here are some libraries that might be used:

- Bech32.sol
- pStake's Bech32.sol
**LiFi:** We validate the address on the backend side, and we don't want to double check in the contract.
**Spearbit:** Acknowledged.
