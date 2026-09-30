# [M] RocketPoolMinipool - should check for address(0x0)

## Summary
Severity: Medium
Source: https://github.com/tintinweb/smart-contract-vulndb
Type: audit-issue

## Details
#### Description

The two implementations for `getContractAddress()` in `Minipool/Delegate` are not checking whether the requested contract's address was ever set before. If it were never set, the method would return `address(0x0)`, which would silently make all `delegatecall`s  succeed without executing any code. In contrast, `RocketBase.getContractAddress()` fails if the requested contract is not known.

It should be noted that this can happen if `rocketMinipoolDelegate` is not set in global storage, or it was cleared afterward, or if `_rocketStorageAddress` points to a contract that implements a non-throwing fallback function (may not even be storage at all).


#### Examples

* Missing checks


**rocketpool-2.5-Tokenomics-updates/contracts/contract/minipool/RocketMinipool.sol:L170-L172**
```solidity
function getContractAddress(string memory _contractName) private view returns (address) {
    return rocketStorage.getAddress(keccak256(abi.encodePacked("contract.address", _contractName)));
}
```


**rocketpool-2.5-Tokenomics-updates/contracts/contract/minipool/RocketMinipoolDelegate.sol:L91-L93**
```solidity
function getContractAddress(string memory _contractName) private view returns (address) {
    return rocketStorage.getAddress(keccak256(abi.encodePacked("contract.address", _contractName)));
}
```

* Checks implemented


**rocketpool-2.5-Tokenomics-updates/contracts/contract/RocketBase.sol:L84-L92**
```solidity
function getContractAddress(string memory _contractName) internal view returns (address) {
    // Get the current contract address
    address contractAddress = getAddress(keccak256(abi.encodePacked("contract.address", _contractName)));
    // Check it
    require(contractAddress != address(0x0), "Contract not found");
    // Return
    return contractAddress;
}

```

#### Recommendation

Similar to `RocketBase.getContractAddress()` require that the contract is set.
