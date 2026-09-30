# [M] Excess ETH not returned in deployDeviceWalletAsAdmin and createAccount

## Summary
Severity: Medium
Contest weight: 0.5965
Dataset id: 7728
Source: https://huggingface.co/datasets/Zaevlad/audit-findings-dataset
Type: audit-finding

## Details
In DeviceWalletFactory.sol, both createAccount() and deployDeviceWalletAsAdmin() functions do not properly return excess ETH when prefunding a DeviceWallet.
```solidity
function deployDeviceWalletAsAdmin(
    string memory _deviceUniqueIdentifier,
    bytes32[2] memory _deviceWalletOwnerKey,
    uint256 _salt,
    uint256 _depositAmount
) public payable onlyAdmin returns (Wallets memory) {
    address deviceWalletAddress = createAccount(
        _deviceUniqueIdentifier,
        _deviceWalletOwnerKey,
        _salt,
        _depositAmount
    );
    ESIMWalletFactory eSIMWalletFactory = registry.eSIMWalletFactory();
    address eSIMWalletAddress = eSIMWalletFactory.deployESIMWallet(deviceWalletAddress, _salt);
    DeviceWallet(payable(deviceWalletAddress)).addESIMWallet(
        eSIMWalletAddress,
        true
    );
    eSIM - report.md
    emit DeviceWalletDeployed(deviceWalletAddress, eSIMWalletAddress, _deviceWalletOwnerKey);
    return Wallets(deviceWalletAddress, eSIMWalletAddress);
}
```
```solidity
function createAccount(
    string memory _deviceUniqueIdentifier,
    bytes32[2] memory _deviceWalletOwnerKey,
    uint256 _salt,
    uint256 _depositAmount
) public payable returns (DeviceWallet deviceWallet) {
    require(
        bytes(_deviceUniqueIdentifier).length != 0,
        "DeviceIdentifier cannot be empty"
    );
    // Check if the device identifier is actually unique
    address wallet = registry.uniqueIdentifierToDeviceWallet(_deviceUniqueIdentifier);
    if (wallet != address(0)) {
        return DeviceWallet(payable(wallet));
    }
    // Check if P256 public key is actually unique
    bytes32 keyHash = keccak256(abi.encode(_deviceWalletOwnerKey[0], _deviceWalletOwnerKey[1]));
    wallet = registry.registeredP256Keys(keyHash);
    if (wallet != address(0)) {
        return DeviceWallet(payable(wallet));
    }
    address addr = address(new BeaconProxy{salt: bytes32(_salt)}(
        abi.encodeCall(
            DeviceWallet.init,
            (_deviceUniqueIdentifier, _deviceWalletOwnerKey)
        )
    ));
    uint256 codeSize = addr.code.length;
    if (codeSize > 0) {
        return DeviceWallet(payable(addr));
    }
    // Prefund the account with msg.value
    if (msg.value > 0 && _depositAmount <= msg.value) {
        entryPoint.depositTo{value: _depositAmount}(addr);
    }
    deviceWallet = DeviceWallet(payable(addr));
}
```
Any excess ETH sent during deployment remains trapped in the factory contract, making it inaccessible to the sender.
We should note a few things.
The function deployDeviceWalletForUsers() correctly tracks and returns excess ETH, but the other two functions do not, leading to an inconsistent user experience.
This function deploys multiple device wallets at once. When the admin calls it, it calls the above two functions accordingly, and the excess ETH is refunded to the admin.
// return unused ETH
if(availableETH > 0) {
    (bool success,) = msg.sender.call{value: availableETH}("");
    require(success, "ETH return failed");
}

## Recommendation
The excess ETH is not refunded only when the admin calls deployDeviceWalletAsAdmin() or a user calls createAccount().
You need to be careful about whether and how you implement the refund of the excess ETH because doing so can break deployDeviceWalletForUsers(), which already refunds the excess ETH and calls the other two functions.
