# [H] The deployLazyWalletAndSetESIMIdentifier function won't send ETH to the registry and will revert, resulting in a core protocol functionality not working

## Summary
Severity: High
Contest weight: 0.7678
Dataset id: 7724
Source: https://huggingface.co/datasets/Zaevlad/audit-findings-dataset
Type: audit-finding

## Details
The LazyWalletRegistry::deployLazyWalletAndSetESIMIdentifier() function is an admin-controlled function that is supposed to deploy a device wallet and eSIM wallet for a certain user.
```solidity
function deployLazyWalletAndSetESIMIdentifier(
    bytes32[2] memory _deviceOwnerPublicKey,
    string calldata _deviceUniqueIdentifier,
    uint256 _salt,
    uint256 _depositAmount
) external payable onlyAdmin {
    require(_depositAmount == msg.value, "Incorrect ETH");
    require(isLazyWalletDeployed(_deviceUniqueIdentifier) == false, "Already deployed");
    (deviceWallet, eSIMWallets) = registry.deployLazyWallet(
        _deviceOwnerPublicKey,
        _deviceUniqueIdentifier,
        _salt,
        eSIMUniqueIdentifiers,
        listOfDataBundleDetails,
        _depositAmount
    );
```
As can be seen from the code snippet above, the function is payable and it requires the msg.value to be equal to the _depositAmount parameter, which is used in the RegistryHelper::deployLazyWallet() function, however, the msg.value won't be transferred to the Registry.sol instance and the function will revert. The RegistryHelper::deployLazyWallet() function also won't transfer any ETH sent to it when the call is made to the DeviceWalletFactory.sol contract, and thus revert as well. This is an important eSIM - report.md protocol functionality, however the functions will always revert if the msg.value sent is bigger than 0 when the call to them is made. This makes core protocol functionality obsolete.

## Recommendation
Consider using the following pattern to transfer the msg.value successfully
```solidity
registry.deployLazyWallet{value:msg.value}(...)
```
