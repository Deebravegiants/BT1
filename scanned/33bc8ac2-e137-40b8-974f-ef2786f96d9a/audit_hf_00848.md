# [M] The UUPS proxie standard is im-

## Summary
Severity: Medium
Contest weight: 0.2099
Dataset id: 2585
Source: https://huggingface.co/datasets/Zaevlad/audit-findings-dataset
Type: audit-finding

## Details
Both the AssetFactory.sol and FlashSwapRouter.sol contracts inherit the UUPSUpgradeable contract from Openzepelin, indicating that the devs of the protocol want to have the possibility of upgrading the above mentioned contracts at some point in the future. Both of the contracts also implement the OwnableUpgradeable contract, and the _authorizeUpgrade() function in both contracts has the onlyOwner modifier. This function is used to check whether the person who tries to update the implementation contract in the Proxy has the required access. However in both contracts the initialize function sets the owner of the contract to the ModuleCore.sol contract as can be seen in the AssetFactory::initialize() and FlashSwapRouter::initialize() functions. The function from the UUPSUpgradeable contract that is used to upgrade the implementation contract in the proxy is the upgradeToAndCall() function, however this function can't be called from the ModuleCore.sol contract is the owner of both the contracts, and there isn't any functionality to transfer the ownership either. Thus AssetFactory.sol and FlashSwapRouter.sol contracts are effectively not upgradable, breaking a very important functionality of the protocol. The upgradeToAndCall() function can't be called from the ModuleCore.sol contract and upgrade the AssetFactory.sol and FlashSwapRouter.sol contracts. Internal pre-conditions 1. All the contracts in the protocol are deployed. External pre-conditions None. Attack Path Contracts that are expected to be upgradable, can't be upgraded due to missing functionality in the ModuleCore.sol contract.

## Recommendation
Implement a call to the upgradeToAndCall() function in the ModuleCore.sol contract.
