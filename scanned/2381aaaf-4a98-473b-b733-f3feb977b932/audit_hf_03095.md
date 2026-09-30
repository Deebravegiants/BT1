# [H] Call and Vault implementations can be arbitrarily changed by anyone.

## Summary
Severity: High
Contest weight: 0.2944
Dataset id: 17469
Source: https://huggingface.co/datasets/Zaevlad/audit-findings-dataset
Type: audit-finding

## Details
Hook protocol uses a beacon proxy pattern for Call and Vault implementations where the proxy gets the implementation address for each call from an upgradeable beacon. However, the beacon initialization function can be called by anyone repeatedly to re-initialize with a malicious beacon and return arbitrary implementations for Calls and Vaults. Hook protocol uses a modified version of OpenZeppelin’s beacon proxy pattern for Call and Vault implementations where the proxy gets the implementation address for each call from an upgradeable beacon. Instead of using a constructor to set the beacon address, the proxy uses an initialization function initializeBeacon to make this pattern usable with Create2 proxy deployments from a factory. However, the beacon initialization function has public visibility without an initializer modifier protection (allowing initialization only once) which means that it can be called by anyone repeatedly to re-initialize with a malicious beacon and return arbitrary implementations for Calls and Vaults. initializeBeacon for Call and Vaults can be called by anyone repeatedly to re-initialize with a malicious beacon and return arbitrary implementations at any point subverting the entire protocol.

## Recommendation
Add support for using the initializer modifier on initializeBeacon so it can be called only once during proxy creation for Calls and Vaults. initializable. This change simply utilizes the OpenZeppelin Initializable library already in use in the protocol. https://github.com/hookart/protocol/pull/47 Follow up to remove Initializable import at L7: https://github.com/hookart/protocol/pull/69 Verified fix.
