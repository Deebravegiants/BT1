# [M] Corrupted storage after upgrade in theMarketFactory

## Summary
Severity: Medium
Contest weight: 0.5760
Dataset id: 23195
Source: https://huggingface.co/datasets/Zaevlad/audit-findings-dataset
Type: audit-finding

## Details
The old MarketFactory is meant to be upgraded to a new implementation. The problem is that a new extensions mapping was added between currently occupied storage slots. After the upgrade, the newly upgraded smart contract would be reading from storage slots that contain data no longer corresponding to the new storage layout. This would cause the system to break in an unpredictable manner, depending on the number of storage slots added as part of the upgrade.
As seen in the old storage layout:
```solidity
IFactory public immutable oracleFactory;
ProtocolParameterStorage private _parameter;
mapping(address => mapping(address => bool)) public operators;
mapping(IOracleProvider => mapping(address => IMarket)) private _markets;
```
And the new storage layout:
```solidity
IFactory public immutable oracleFactory;
IVerifier public immutable verifier;
ProtocolParameterStorage private _parameter;
mapping(address => bool) public extensions;
mapping(address => mapping(address => bool)) public operators;
mapping(IOracleProvider => mapping(address => IMarket)) private _markets;
mapping(address => mapping(address => bool)) public signers;
```
The storage will be corrupted after the upgrade because the new extensions mapping was introduced between already populated slots. The extensions, operators, _markets, and _referralFees will read and write to incorrect slots.
• Corrupted storage of the MarketFactory contract.
• System would break in an unpredictable manner.

## Recommendation
Place the extensions mapping after the _referralFees mapping so that both extensions and signers are added after all the occupied slots, avoiding storage corruption.
