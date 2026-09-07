# [M] EVM's `ecrecover` is susceptible to signature malleability

## Summary
Severity: Medium
Chain: Smart contract
Component: Catalyst-Exchange
Published: 2024-01-24
Source: https://github.com/hats-finance/Catalyst-Exchange-0x3026c1ea29bf1280f99b41934b2cb65d053c9db4/issues/3
Type: hats-finding

## Details
**Github username:** @0xfuje
**Twitter username:** 0xfuje
**Submission hash (on-chain):** 0x45c350f639294143f07190bbce288c6f36fbac4941a74a2e52d8c19db5e88ec1
**Severity:** medium

**Description:**
## Impact
Potential replay attacks, attacker could forge `ecrecover` return value to match guardian signatures

## Description
The attacker could flip `s` and `v` values to create a different signature that equals to the same hash & signer. There are three instances of `ecrecover` in the codebase:

`src/apps/mock/IncentivizedMockEscrow.sol`
```solidity
53:		address messageSigner = ecrecover(keccak256(_message), v, r, s);
```

`src/apps/wormhole/external/callworm/WormholeVerifier.sol`
```solidity
102:	address signatory = ecrecover(hash, v, r, s);
```

`src/apps/wormhole/external/wormhole/Messages.sol`
```solidity
116:	address signatory = ecrecover(hash, sig.v, sig.r, sig.s);
```



## Recommendation
Instead of the vulnerable `ecrecover` consider using Openzeppelin's `ECDSA` library: [`openzeppelin-contracts/utils/cryptography/ECDSA.sol`](https://github.com/OpenZeppelin/openzeppelin-contracts/blob/master/contracts/utils/cryptography/ECDSA.sol)
