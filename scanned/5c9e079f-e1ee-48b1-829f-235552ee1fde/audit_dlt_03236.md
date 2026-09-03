# [H] `addRewardToken()` does note remove old entries before adding new ones

## Summary
Severity: High
Chain: Smart contract
Component: 2022-01-dev-test-repo
Published: 2023-12-20
Source: https://github.com/code-423n4/2022-01-dev-test-repo-findings/issues/385
Type: code-finding

## Details
### Lines of code

--------------

[455](https://github.com/Tapioca-DAO/tap-token-audit/blob/59749be5bc2286f0bdbf59d7ddc258ddafd49a9f/contracts/governance/twTAP.sol#L455-L460), [280](https://github.com/Tapioca-DAO/tap-token-audit/blob/59749be5bc2286f0bdbf59d7ddc258ddafd49a9f/contracts/options/TapiocaOptionLiquidityProvision.sol#L280-L293), [378](https://github.com/Tapioca-DAO/tapioca-bar-audit/blob/2286f80f928f41c8bc189d0657d74ba83286c668/contracts/Penrose.sol#L378-L388), [411](https://github.com/Tapioca-DAO/tapioca-bar-audit/blob/2286f80f928f41c8bc189d0657d74ba83286c668/contracts/Penrose.sol#L411-L421)

### Vulnerability details

-------------

Each time `addRewardToken()` is called, new entries are added to the array, but doing so does not remove any old entries. By calling the function multiple times, an attacker can can increase their voting power indefinitely, without having to acquire new tokens.

```solidity
File: contracts/governance/twTAP.sol

455      function addRewardToken(IERC20 token) external onlyOwner returns (uint256) {
456          uint256 i = rewardTokens.length;
457          rewardTokens.push(token);
458          rewardTokenIndex[token] = i;
459          return i;
460:     }

```



```solidity
File: contracts/options/TapiocaOptionLiquidityProvision.sol

280      ) external onlyOwner updateTotalSGLPoolWeights {
281          require(assetID > 0, "tOLP: invalid asset ID");
282          require(
283              activeSingularities[singularity].sglAssetID == 0,
284              "tOLP: already registered"
285          );
286  
287          activeSingularities[singularity].sglAssetID = assetID;
288          activeSingularities[singularity].poolWeight = weight > 0 ? weight : 1;
```

_Trimmed to 38 lines — full report: https://github.com/code-423n4/2022-01-dev-test-repo-findings/issues/385_
