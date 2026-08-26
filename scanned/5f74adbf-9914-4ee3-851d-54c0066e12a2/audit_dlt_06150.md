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
```

_Trimmed to 38 lines — full report: https://github.com/hats-finance/StakeWise-0xd91cd6ed6c9a112fdc112b1a3c66e47697f522cd/issues/3_
