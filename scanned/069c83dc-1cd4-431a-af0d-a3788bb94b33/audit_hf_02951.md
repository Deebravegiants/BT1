# [M] Missing authorization in the collectFees can lead to sandwich

## Summary
Severity: Medium
Contest weight: 0.2372
Dataset id: 16367
Source: https://huggingface.co/datasets/Zaevlad/audit-findings-dataset
Type: audit-finding

## Details
The collectFees function performs following operations for every input token Id: It collects fees via _collectFeesUniV3. It swaps tokens to Volt tokens via _swapToVolt. Lastly, it transfer Volt tokens into staking contract via _transferVoltToStakingVault. Each of this operation can be done individually respectively via collectFeesOnly, swapToVoltOnly, transferToVaultOnly functions. All of these three functions are protected by the onlyRole(DEFAULT_ADMIN_ROLE) modifier, whereas the collectFees has no authorisation applied at all. The _swapToVolt function has no slippage applied (uint256 amountOutMin = 0;). Thus, the swap will be done for any possible ratio between pair's tokens. A malicious user can leverage this fact and trigger collectFees to sandwich it and manipulate the price of pair before fees collection and after to collect potential profits. However, the success of attack depends on several factors, including: whether Uniswapv2 or Uniswapv3 is targeted, what is the liquidity provided to the Uniswapv3's pool, what is the amount of fee collected by the protocol in prior of the swap. /// @notice Collect fees, swap to `$VOLT` tokens, and transfer to `IStakingVault` instance function collectFees(uint256[] calldata tokenIds) external { if (tokenIds.length > MAX_COLLECT_FEES_BATCH_SIZE) revert PositionManagerArrayTooLong(); for (uint256 i = 0; i < tokenIds.length; i++) { uint256 tokenId = tokenIds[i]; VoltStakingReport.md if (!_uniV3NftIdIsManaged[tokenId]) revert PositionManagerUniswapV3PositionNotManaged(tokenId); (uint256 amount0, uint256 amount1) = _collectFeesUniV3(tokenId); emit PositionFeesCollected(tokenId); UniV3Nft memory nft = _getNftUniV3(tokenId); _swapToVolt(nft.token0, amount0); emit TokenToVoltSwapped(nft.token0); _swapToVolt(nft.token1, amount1); emit TokenToVoltSwapped(nft.token1); _transferVoltToStakingVault();

## Recommendation
Consider enhancing the collectFees function either with the authorisation done for privileged account only or by introducing internal slippage preventing large deviation within swaps.
