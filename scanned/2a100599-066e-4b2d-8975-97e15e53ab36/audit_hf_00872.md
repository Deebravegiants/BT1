# [H] V2AMO is not compatible with

## Summary
Severity: High
Contest weight: 0.7844
Dataset id: 2626
Source: https://huggingface.co/datasets/Zaevlad/audit-findings-dataset
Type: audit-finding

## Details
According to the docs, the Dex scope for V2 includes Velodrome/Aerodrome. We expect the V2 tech-implementation work with the “classic” pools on the following Dexes: Velodrome, Aerodrome, Thena, Equalizer (Fantom/Sonic/Base), Ramses and forks (legacy pools), Tokan However, for Velodrome/Aerodrome implementations, the current V2AMO is not compatible. There are two parts of integration with Velodrome/Aerodrome that are buggy: 1. Gauge 2. Router the same code, I will only post Aerodrome code): 1. Gauge The main difference is in the getReward() function. Aerodrome interface: https://github.com/aerodrome-finance/contracts/blob/main/contracts/interfaces/IGauge.sol
```solidity
interface IGauge {
    function getReward(address _account) external;
}
```
liquidity-amo/contracts/interfaces/v2/IGauge.sol#L4
```solidity
interface IGauge {
    function getReward(address account, address[] memory tokens) external;
    function getReward(uint256 tokenId) external;
    function getReward() external;
}
```
2. Router The main difference is: 1. Aerodrome uses poolFor instead of pairFor when querying a pool/pair. Aerodrome interface: https://github.com/aerodrome-finance/contracts/blob/main/contracts/interfaces/IRouter.sol#L6
```solidity
interface IRouter {
    struct Route {
        address from;
        address to;
        bool stable;
        address factory;
    }
    function poolFor(
        address tokenA,
        address tokenB,
        bool stable,
        address _factory
    ) external view returns (address pool);
    function swapExactTokensForTokens(
        uint256 amountIn,
        uint256 amountOutMin,
        Route[] calldata routes,
        address to,
        uint256 deadline
    ) external returns (uint256[] memory amounts);
}
```
liquidity-amo/contracts/interfaces/v2/IRouter.sol#L4
```solidity
interface IRouter {
    struct route {
        address from;
        address to;
        bool stable;
    }
    function pairFor(address tokenA, address tokenB, bool stable) external view returns (address pair);
    function swapExactTokensForTokens(
        uint256 amountIn,
        uint256 amountOutMin,
        route[] memory routes,
        address to,
        uint256 deadline
    ) external returns (uint256[] memory amounts);
}
```
Internal pre-conditions N/A External pre-conditions N/A Attack Path N/A V2AMO does not work with Aerodrome/Velodrome as expected.

## Recommendation
N/A
