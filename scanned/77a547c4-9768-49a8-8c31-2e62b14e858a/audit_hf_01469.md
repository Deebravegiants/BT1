# [C] Frontrunning Attack Leading to Permanent ETH Loss in createAccount

## Summary
Severity: Critical
Contest weight: 0.4099
Dataset id: 7708
Source: https://huggingface.co/datasets/Zaevlad/audit-findings-dataset
Type: audit-finding

## Details
The createAccount() function in DeviceWalletFactory.sol allows users to deploy a new DeviceWallet and prefund it with ETH.
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
However, an attacker can front-run a victimʼs transaction by deploying the wallet first. This causes the victim's transaction to return the already deployed wallet without executing the ETH deposit.
// Check if the device identifier is actually unique
registry.uniqueIdentifierToDeviceWallet(_deviceUniqueIdentifier);
return DeviceWallet(payable(wallet));
As a result, the victim's ETH remains permanently locked in the factory contract.
eSIM - report.md
Attack Vector
- The victim sends a transaction to createAccount() with _deviceUniqueIdentifier, _deviceWalletOwnerKey, and _depositAmount, and also sends ETH to prefund the wallet.
- The attacker sees the transaction in the mempool and submits the same createAccount() call with:
  - The same _deviceUniqueIdentifier and _deviceWalletOwnerKey
  - Higher gas fees to ensure their transaction executes first.
- The attackerʼs transaction executes first, successfully deploying the wallet without depositing ETH.
- Victimʼs transaction executes second and reaches this check:
  registry.uniqueIdentifierToDeviceWallet(_deviceUniqueIdentifier);
  return DeviceWallet(payable(wallet));
  Since the wallet already exists, the function returns the attacker's deployed wallet instead of deploying a new one.
- However, the victim has already sent ETH, which is now stuck in the factory contract forever.
A malicious user can do this attack constantly. This would only cost him the price of the gas, while the honest user would lose all his ETH.

## Recommendation
Revert the transactions if ETH is sent, but Wallet already exists.
```solidity
require(msg.value == 0, "ETH will be lost if wallet already exists");
return DeviceWallet(payable(existingWallet));
```
The other option is to return the ETH if the Wallet already exists.
In this way, the honest user will not lose funds, and the attack will be rendered meaningless.
