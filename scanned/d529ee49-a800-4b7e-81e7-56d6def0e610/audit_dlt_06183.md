# [M] Safe multisig threshold of one is unsafe

## Summary
Severity: Medium
Chain: Smart contract
Component: SafeStaking-by-HOPR
Published: 2023-10-08
Source: https://github.com/hats-finance/SafeStaking-by-HOPR-0x607386df18b663cf5ee9b879fbc1f32466ad5a85/issues/21
Type: hats-finding

## Details
**Github username:** @0xfuje
**Submission hash (on-chain):** 0xe897b2aa880d18df7810069cf66f577415e62acbf0ce56d8375a701da6c32114
**Severity:** medium

**Description:**
## Description
Comment from the sponsor:
> Since one major goal of SafeStaking is to minimize damage when a node key is compromised, exploits which involve access to private keys ARE in scope. However, the following related issues are out of scope:
>  - Loss of funds directly controlled by the compromised key
>   - Situations where an attacker gains access to ALL keys needed to fully control the Safe and associated node (i.e., m of n owner keys of an m or n safe)

The root of the problem is that the default `Safe` deployed for node management uses a hardcoded multisig threshold of 1 and there is no setting at initialization to setup a higher threshold (see `NodeStakeFactory` - `clone()`). Threshold of one can't be considered multisig and is very unsafe. Since the above comment private key compromises are in scope: an attacker only needs to gain access to one key of admins to gain the control of `Safe` and cause irreversible damage.

`src/node-stake/NodeStakeFactory.sol` - [`clone()`](https://github.com/hats-finance/SafeStaking-by-HOPR-0x607386df18b663cf5ee9b879fbc1f32466ad5a85/blob/master/packages/ethereum/contracts/src/node-stake/NodeStakeFactory.sol#L83-L143)
```solidity
        // Prepare safe initializer data
        bytes memory safeInitializer = abi.encodeWithSignature(
            "setup(address[],uint256,address,bytes,address,address,uint256,address)",
            admins,
            1, // threshold
            address(0),
            hex"00",
            SafeSuiteLib.SAFE_CompatibilityFallbackHandler_ADDRESS,
            address(0),
            0,
            address(0)
        );

        // 2. Deploy Safe proxy
        SafeProxy safeProxy = SafeProxyFactory(SafeSuiteLib.SAFE_SafeProxyFactory_ADDRESS).createProxyWithNonce(
            SafeSuiteLib.SAFE_Safe_ADDRESS, safeInitializer, nonce
        );
```
End users can theoretically change the threshold later in `Safe`, however it's likely that they either don't know about it since it's not documented or just leave the default threshold at 1.

In my Proof of Concept I demonstrate how an attacker that gains access to one of the admin's private key can take control of `Safe`, renounce other admin's ownership, transfer `Safe` funds to himself and take ownership of `HoprNodeManagementModule`

## Proof of Concept

_Trimmed to 38 lines — full report: https://github.com/hats-finance/SafeStaking-by-HOPR-0x607386df18b663cf5ee9b879fbc1f32466ad5a85/issues/21_
