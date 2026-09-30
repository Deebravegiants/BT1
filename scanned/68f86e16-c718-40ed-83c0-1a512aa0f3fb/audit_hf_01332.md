# [C] Codeup::claimCodeupERC20() may be forever DoSed by creating the Uniswap pool before it is called

## Summary
Severity: Critical
Contest weight: 0.5385
Dataset id: 6635
Source: https://huggingface.co/datasets/Zaevlad/audit-findings-dataset
Type: audit-finding

## Details
UP-C01 up::claimCodeupERC20() may be forever DoSed by creating the Uniswap pool before it is called Uniswap pools may be created without the underlying tokens existence, which means that up::claimCodeupERC20() is ever called, making it revert when UniswapV2Factory::createPair() is called as the pool has already been created.

## Recommendation
UniswapV2Router::addLiquidity() creates the pool if it does not yet exist, so there is not need to directly create it. The only concern is setting the uniswapV2Pool variable, which may be performed for example by doing:
```solidity
if (uniswapV2Pool == address(0)) {
// added liquidity
uniswapV2Pool = IUniswapV2Factory(uniswapV2Factory).getPair(
wethMemory,
codeupERC20Memory
);
emit PoolCreated(uniswapV2Pool);
}
```
