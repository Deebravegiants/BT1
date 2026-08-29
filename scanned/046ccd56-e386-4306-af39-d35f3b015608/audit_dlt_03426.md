# [M] `Keepers` does not implement EIP712 correctly on multiple occasions

## Summary
Severity: Medium
Chain: Smart contract
Component: 2024-04-noya
Published: 2024-05-17
Source: https://github.com/code-423n4/2024-04-noya-findings/issues/1428
Type: code-finding

## Details
# Lines of code

https://github.com/code-423n4/2024-04-noya/blob/main/contracts/governance/Keepers.sol#L11
https://github.com/code-423n4/2024-04-noya/blob/main/contracts/governance/Keepers.sol#L100
https://github.com/code-423n4/2024-04-noya/blob/main/contracts/governance/Keepers.sol#L102


# Vulnerability details

### **Problem 1**

The implementation of the `txInputHash` ([here](https://github.com/code-423n4/2024-04-noya/blob/9c79b332eff82011dcfa1e8fd51bad805159d758/contracts/governance/Keepers.sol#L100)) is incorrect. The parameter `data`, which is of type `bytes`, is used in the hash. According to EIP712, this is considered a `dynamic type`. Dynamic types must be hashed with `keccak256` to become a single 32-byte word before being encoded and hashed with the `typeHash` and other values.

```
bytes32 txInputHash =
	  keccak256(abi.encode(TXTYPE_HASH, nonce, destination, data, gasLimit, executor, deadline));
```

### **Problem 2**

`TXTYPE_HASH` is hashed with incorrect definition of typed structured data ([here](https://github.com/code-423n4/2024-04-noya/blob/9c79b332eff82011dcfa1e8fd51bad805159d758/contracts/governance/Keepers.sol#L12)). The last parameter is split by ' ,'. However, according to EIP712, the parameters of the `typeHash` should be split only by ','.

```
bytes32 public constant TXTYPE_HASH = keccak256(
    "Execute(uint256 nonce,address destination,bytes data,uint256 gasLimit,address executor, uint256 deadline)"
); 
```

### Improvement 1

In `Keepers.execute()`, replace `bytes32 totalHash = keccak256(abi.encodePacked("\\x19\\x01", _domainSeparatorV4(), txInputHash));` with `_hashTypedDataV4` ([here](https://github.com/code-423n4/2024-04-noya/blob/9c79b332eff82011dcfa1e8fd51bad805159d758/contracts/governance/Keepers.sol#L102)).

```diff
bytes32 txInputHash =
  keccak256(abi.encode(TXTYPE_HASH, nonce, destination, data, gasLimit, executor, deadline));

- bytes32 totalHash = keccak256(abi.encodePacked("\x19\x01", _domainSeparatorV4(), txInputHash));
+ bytes32 totalHash = _hashTypedDataV4(txInputHash);
```

_Trimmed to 38 lines — full report: https://github.com/code-423n4/2024-04-noya-findings/issues/1428_
