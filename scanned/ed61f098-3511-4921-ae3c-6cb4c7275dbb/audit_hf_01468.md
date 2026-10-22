# [C] Malicious but registered Device Wallet can steal an eSIM Wallet

## Summary
Severity: Critical
Contest weight: 0.4763
Dataset id: 7707
Source: https://huggingface.co/datasets/Zaevlad/audit-findings-dataset
Type: audit-finding

## Details
The updateDeviceWalletAssociatedWithESIMWallet() function in Registry.sol links an eSIM
wallet to a specific device wallet.

```solidity
function updateDeviceWalletAssociatedWithESIMWallet(
) external onlyDeviceWallet {
    isESIMWalletValid[_eSIMWalletAddress] = _deviceWalletAddress;
    emit UpdatedDeviceWalletassociatedWithESIMWallet(_eSIMWalletAddress,
_deviceWalletAddress);
```

The function has a modifier that ensures that only valid Device Wallets can call this function:

```solidity
modifier onlyDeviceWallet() {
    if(isDeviceWalletValid[msg.sender] != true) revert Errors.OnlyDeviceWallet();
}
```

The problem here is that updateDeviceWalletAssociatedWithESIMWallet() currently lacks an
ownership check, meaning any valid Device Wallet could potentially link itself to any eSIM Wallet, even if
that eSIM Wallet is already linked to another device.
For example:
- Alice owns an eSIM Wallet (0xESIM1), linked to her device (0xDeviceAlice).
- Bob, a malicious actor, has a registered Device Wallet (0xDeviceBob).
- Bob calls: updateDeviceWalletAssociatedWithESIMWallet(0xESIM1, 0xDeviceBob);
- Aliceʼs eSIM Wallet is now controlled by Bobʼs device.
- Bob gains control over Aliceʼs eSIM wallet.
This allows a malicious but registered Device Wallet to steal an eSIM Wallet by reassigning it.

## Recommendation
Ensure that only the current owner (device) of an eSIM Wallet can update it or that only unlinked eSIM
wallets can be assigned to a new device. This will prevent overriding an existing association:

```solidity
require(
    isESIMWalletValid[_eSIMWalletAddress] == msg.sender,
    "Unauthorised caller or already assigned"
)
```
