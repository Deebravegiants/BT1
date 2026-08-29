# [M] Possible to front-run safe setup and inject malicious module

## Summary
Severity: Medium
Chain: Smart contract
Component: SafeStaking-by-HOPR
Published: 2023-10-08
Source: https://github.com/hats-finance/SafeStaking-by-HOPR-0x607386df18b663cf5ee9b879fbc1f32466ad5a85/issues/22
Type: hats-finding

## Details
**Github username:** @0xfuje
**Submission hash (on-chain):** 0xc9354e7b55ec27d7667c218c39e99c695b21c118f66b95d9eddb42bf733d615d
**Severity:** medium

**Description:**
## Impact
`Safe` can be compromised with user funds stolen, malicious module can make variety of damages

## Description
A malicious actor could front-run a `Safe` setup with the same `nonce` and inject a malicious module to the setup that could compromise funds and make authorized actions. A user's transaction will fail, but he might think it's somehow succeeded since he will see that he has ownership of a `Safe` with the same `admins`. If he starts using the malicious `Safe`, his funds can be compromised and the module can make other damages via using restricted functions reserved for `Safe`.

The problem that allows the vulnerability is the arbitrary address input of `moduleSingletonAddress` in `NodeStakeFactory` - `clone()` and that there is no validation that this address is in fact the intended `HoprNodeManagementModule` contract.

`src/node-stake/NodeStakeFactory.sol` - [`clone()`](https://github.com/hats-finance/SafeStaking-by-HOPR-0x607386df18b663cf5ee9b879fbc1f32466ad5a85/blob/master/packages/ethereum/contracts/src/node-stake/NodeStakeFactory.sol#L83-L91)
```solidity
    function clone(
        address moduleSingletonAddress, // @audit arbitrary address
        address[] memory admins,
        uint256 nonce,
        bytes32 defaultTarget
    )
        public
        returns (address, address payable)
    {
```
The malicious module will be enabled to be used in `Safe` later in the function:
```solidity
	// Enable the node management module
	bytes  memory enableModuleData = abi.encodeWithSignature("enableModule(address)", moduleProxy);
	prepareSafeTx(Safe(safeProxyAddr), 0, enableModuleData);
```
--- 
### Front-run admins
Note that a similar attack is possible via front-running where the attacker injects his address as one of the admin addresses in the setup. Later he can take ownership of the `Safe` and renounce other owners.

## Proof of Concept
1. navigate to `packages/ethereum/contracts/test/NodeStakeFactory.t.sol`
2. copy and paste the below proof of concept inside `HoprNodeStakeFactoryTest` contract

_Trimmed to 38 lines — full report: https://github.com/hats-finance/SafeStaking-by-HOPR-0x607386df18b663cf5ee9b879fbc1f32466ad5a85/issues/22_
