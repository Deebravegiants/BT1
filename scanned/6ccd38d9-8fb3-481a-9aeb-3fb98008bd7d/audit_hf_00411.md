# [M] Restored addresses will not be

## Summary
Severity: Medium
Contest weight: 0.4504
Dataset id: 1813
Source: https://huggingface.co/datasets/Zaevlad/audit-findings-dataset
Type: audit-finding

## Details
When an address is restored after being deleted due to being compromised, it remains marked as compromised in the isAddressCompromised mapping. This prevents the address from taking any actions on behalf of the profile, even though it should be able to.
When an address is compromised, it can be deleted by calling EthosProfile::deleteAddressAtIndex(), which marks the address as compromised in the isAddressCompromised mapping.
```solidity
function deleteAddressAtIndex(uint256 addressIndex) external whenNotPaused {
    isAddressCompromised[addressStr] = true;
}
```
The purpose of the isAddressCompromised mapping is to ensure that no address marked as compromised and deleted can take any action on behalf of the profile. If a previously deleted address is no longer compromised, it can be restored when an address associated with the same profile as the deleted address calls EthosProfile::registerAddress() and provides that address.
However, the address is not unmarked in isAddressCompromised, meaning that restored addresses will still be unable to take any actions on behalf of the profile as they remain flagged as compromised.
Attack Path
1. AddressA calls EthosProfile::registerAddress() to register AddressB.
2. AddressB is compromised.
3. AddressA calls EthosProfile::deleteAddressAtIndex() to delete AddressB and mark it as compromised in isAddressCompromised.
4. AddressB is no longer compromised.
5. AddressA calls EthosProfile::registerAddress() to restore AddressB.
6. AddressB remains marked as compromised in isAddressCompromised and cannot act on behalf of the profile, even though it should be able to.
A previously deleted address will not be able to take any action on behalf of the profile when restored, as it remains marked as compromised.

## Recommendation
Consider unmarking addresses as compromised when they are restored. If it is necessary to store the addresses that were removed in the past, this should be managed with a separate mapping.
