# [M] EIP-712 typehash is incorrect in `KeeperRewards.sol` and `KeeperValidators.sol`

## Summary
Severity: Medium
Chain: Smart contract
Component: StakeWise
Published: 2023-08-21
Source: https://github.com/hats-finance/StakeWise-0xd91cd6ed6c9a112fdc112b1a3c66e47697f522cd/issues/3
Type: hats-finding

## Details
**Github username:** @milotruck
**Submission hash (on-chain):** 0xbe4be2aa1e9d3642d9cc232474a3be3f75701d295d95745b67d0cda9ce8df7a7
**Severity:** medium

**Description:**
## Bug Description

In `KeeperRewards.sol`, `updateRewards()` verifies signatures according to the [EIP-712](https://eips.ethereum.org/EIPS/eip-712) standard:

[KeeperRewards.sol#L92-L106](https://github.com/stakewise/v3-core/blob/main/contracts/keeper/KeeperRewards.sol#L92-L106)

```solidity
    // verify rewards update signatures
    _verifySignatures(
      rewardsMinOracles,
      keccak256(
        abi.encode(
          _rewardsUpdateTypeHash,
          params.rewardsRoot,
          keccak256(bytes(params.rewardsIpfsHash)),
          params.avgRewardPerSecond,
          params.updateTimestamp,
          nonce
        )
      ),
      params.signatures
    );
```

`params.rewardsIpfsHash` is a `string` in the `RewardsUpdateParams` struct:

[IKeeperRewards.sol#L79-L85](https://github.com/stakewise/v3-core/blob/main/contracts/interfaces/IKeeperRewards.sol#L79-L85)

```solidity
  struct RewardsUpdateParams {
    bytes32 rewardsRoot;
    uint256 avgRewardPerSecond;
    uint64 updateTimestamp;
    string rewardsIpfsHash;
    bytes signatures;
  }
```

However, `_rewardsUpdateTypeHash`, which is the function's EIP-712 typehash, incorrectly declares `rewardsIpfsHash` as `bytes32` instead:

[KeeperRewards.sol#L19-L22](https://github.com/stakewise/v3-core/blob/main/contracts/keeper/KeeperRewards.sol#L19-L22)

```solidity
  bytes32 private constant _rewardsUpdateTypeHash =
    keccak256(
      'KeeperRewards(bytes32 rewardsRoot,bytes32 rewardsIpfsHash,uint256 avgRewardPerSecond,uint64 updateTimestamp,uint64 nonce)'
    );
```

Similarly, in `KeeperValidators.sol`, `approveValidators()` uses EIP-712 to verify signatures as well:

[KeeperValidators.sol#L56-L69](https://github.com/stakewise/v3-core/blob/main/contracts/keeper/KeeperValidators.sol#L56-L69)

```solidity
    // verify oracles approved registration
    _verifySignatures(
      validatorsMinOracles,
      keccak256(
        abi.encode(
          _registerValidatorsTypeHash,
          params.validatorsRegistryRoot,
          msg.sender,
          keccak256(params.validators),
          keccak256(bytes(params.exitSignaturesIpfsHash))
        )
      ),
      params.signatures
    );
```

As seen below, in the `ApprovalParams` struct, `params.validators` is declared as `bytes` and `params.exitSignaturesIpfsHash` is a `string`:

[IKeeperValidators.sol#L56-L61](https://github.com/stakewise/v3-core/blob/main/contracts/interfaces/IKeeperValidators.sol#L56-L61)

```solidity
  struct ApprovalParams {
    bytes32 validatorsRegistryRoot;
    bytes validators;
    bytes signatures;
    string exitSignaturesIpfsHash;
  }
```

However, in `_registerValidatorsTypeHash`, `validators` and `exitSignaturesIpfsHash` are incorrectly declared as `bytes32`:

[KeeperValidators.sol#L17-L20](https://github.com/stakewise/v3-core/blob/main/contracts/keeper/KeeperValidators.sol#L17-L20)

```solidity
  bytes32 private constant _registerValidatorsTypeHash =
    keccak256(
      'KeeperValidators(bytes32 validatorsRegistryRoot,address vault,bytes32 validators,bytes32 exitSignaturesIpfsHash)'
    );
```

## Impact

Due to the use of incorrect typehashes, the signature verification in the functions listed above is not [EIP-712](https://eips.ethereum.org/EIPS/eip-712) compliant. 

Contracts or dapps/backends that use "correct" typehashes with correct types for the parameters of these functions will end up generating different signatures, causing them to revert when called.

## Recommended Mitigation

Amend the typehashes shown above to have matching parameters with their respective functions:

`_rewardsUpdateTypeHash`:

```solidity
  bytes32 private constant _rewardsUpdateTypeHash =
    keccak256(
      'KeeperRewards(bytes32 rewardsRoot,string rewardsIpfsHash,uint256 avgRewardPerSecond,uint64 updateTimestamp,uint64 nonce)'
    );
```

`_registerValidatorsTypeHash`:

```solidity
  bytes32 private constant _registerValidatorsTypeHash =
    keccak256(
      'KeeperValidators(bytes32 validatorsRegistryRoot,address vault,bytes validators,string exitSignaturesIpfsHash)'
    );
```
