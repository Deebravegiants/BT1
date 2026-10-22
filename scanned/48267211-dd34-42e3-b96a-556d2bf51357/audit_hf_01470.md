# [H] Device wallet creation can be DoSed, making the whole protocol obsolete

## Summary
Severity: High
Contest weight: 0.7693
Dataset id: 7719
Source: https://huggingface.co/datasets/Zaevlad/audit-findings-dataset
Type: audit-finding

## Details
The DeviceWalletFactory::createAccount() function is permissionless, and it is responsible for deploying and registering the device wallets. The function takes 4 different parameters one of which is a string _deviceUniqueIdentifier. There are several checks that are performed in order to see whether a device wallet with the same parameters has already been registered.
```solidity
registry.uniqueIdentifierToDeviceWallet(_deviceUniqueIdentifier);
return DeviceWallet(payable(wallet));
```
A malicious user can frontrun the admin restricted DeviceWalletFactory::deployDeviceWalletAsAdmin() function, which internally calls the DeviceWalletFactory::createAccount() function, by calling the DeviceWalletFactory::createAccount() function with the same _deviceUniqueIdentifier parameter but a different bytes32[2] memory _deviceWalletOwnerKey parameter. A call to the DeviceWalletFactory::createAccount() function can also be frontrun. A DeviceWallet will be created however the owners will be different. Given the fact that the main purpose of the protocol is to allow users to create DeviceWallets and interact with them, dosing the creation of wallets by paying only the transaction fees is a vulnerability with high severity. This attack can also be utilized to DOS the LazyWalletRegistry::batchPopulateHistory() and LazyWalletRegistry::deployLazyWalletAndSetESIMIdentifier() functions.

## Recommendation
Consider whether the uniqueIdentifierToDeviceWallet mapping is necessary.
Also, consider binding salt to msg.sender to prevent unauthorized deployments:
```solidity
function createAccount(
    string memory _deviceUniqueIdentifier,
    bytes32[2] memory _deviceWalletOwnerKey,
    uint256 _salt,
    uint256 _depositAmount
) public payable returns (DeviceWallet deviceWallet) {
    bytes32 uniqueSalt = keccak256(abi.encodePacked(msg.sender, _salt));
    _deviceUniqueIdentifier, uniqueSalt);
```
eSIM - report.md
