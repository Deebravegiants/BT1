# [M] The owner is a single point of failure and a centralization risk

## Summary
Severity: Medium
Chain: Smart contract
Component: Catalyst-Exchange
Published: 2024-01-24
Source: https://github.com/hats-finance/Catalyst-Exchange-0x3026c1ea29bf1280f99b41934b2cb65d053c9db4/issues/23
Type: hats-finding

## Details
**Github username:** @saidqayoumsadat
**Twitter username:** saqsadat143
**Submission hash (on-chain):** 0x2bf62b1934129003366ed13bf8720d10490b1108e32214242e63b929ab8b10be
**Severity:** medium

**Description:**
**Description**\
Having a single EOA as the only owner of contracts is a large centralization risk and a single point of failure. A single private key may be taken in a hack, or the sole holder of the key may become unable to retrieve the key when necessary, or the single owner can become malicious and perform a rug-pull. Consider changing to a multi-signature setup, and or having a role-based authorization model.

1. **Proof of Concept (PoC) File**


```solidity
file: src/CatalystChainInterface.sol

163    function setMinGasFor(bytes32 chainIdentifier, uint48 minGas) override external onlyOwner {

175    function setMaxUnderwritingDuration(uint256 newMaxUnderwriteDuration) onlyOwner override external {    

```
https://github.com/catalystdao/catalyst/blob/27b4d0a2bca177aff00def8cd745623bfbf7cb6b/evm/src/CatalystChainInterface.sol#L163C1-L163C96


```solidity
file: /CatalystChainInterface.sol

249    function connectNewChain(bytes32 chainIdentifier, bytes calldata remoteCCI, bytes calldata remoteGARP) onlyOwner checkBytes65Address(remoteCCI) override external {

```
https://github.com/catalystdao/catalyst/blob/27b4d0a2bca177aff00def8cd745623bfbf7cb6b/evm/src/CatalystChainInterface.sol#L249C1-L249C168


```solidity
file: /src/CatalystVaultCommon.sol

361    function setFeeAdministrator(address administrator) public override onlyFactoryOwner {

```

_Trimmed to 38 lines — full report: https://github.com/hats-finance/Catalyst-Exchange-0x3026c1ea29bf1280f99b41934b2cb65d053c9db4/issues/23_
