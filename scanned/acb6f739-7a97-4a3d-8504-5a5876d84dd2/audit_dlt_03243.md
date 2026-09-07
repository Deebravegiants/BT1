# [M] Proxy's logic contract relies on code in the constructor

## Summary
Severity: Medium
Chain: Smart contract
Component: 2022-01-dev-test-repo
Published: 2023-12-19
Source: https://github.com/code-423n4/2022-01-dev-test-repo-findings/issues/361
Type: code-finding

## Details
### Lines of code

--------------

[122](https://github.com/Tapioca-DAO/tapiocaz-audit/blob/bcf61f79464cfdc0484aa272f9f6e28d5de36a8f/contracts/Balancer.sol#L122-L131), [50](https://github.com/Tapioca-DAO/tapiocaz-audit/blob/bcf61f79464cfdc0484aa272f9f6e28d5de36a8f/contracts/tOFT/BaseTOFT.sol#L50-L78), [25](https://github.com/Tapioca-DAO/tapiocaz-audit/blob/bcf61f79464cfdc0484aa272f9f6e28d5de36a8f/contracts/tOFT/modules/BaseTOFTLeverageModule.sol#L25-L43), [67](https://github.com/Tapioca-DAO/tap-token-audit/blob/59749be5bc2286f0bdbf59d7ddc258ddafd49a9f/contracts/Vesting.sol#L67-L73), [98](https://github.com/Tapioca-DAO/tapioca-bar-audit/blob/2286f80f928f41c8bc189d0657d74ba83286c668/contracts/markets/bigBang/BigBang.sol#L98-L98), [67](https://github.com/Tapioca-DAO/tapioca-bar-audit/blob/2286f80f928f41c8bc189d0657d74ba83286c668/contracts/usd0/BaseUSDO.sol#L67-L80), [22](https://github.com/Tapioca-DAO/tapioca-bar-audit/blob/2286f80f928f41c8bc189d0657d74ba83286c668/contracts/usd0/modules/USDOLeverageModule.sol#L22-L25)

### Vulnerability details

-------------

Logic contracts cannot rely on code in their constructors, because proxy contracts do not re-execute the logic contract's constructor - only its [initializer](https://docs.openzeppelin.com/upgrades-plugins/1.x/proxies#the-constructor-caveat). Move all code in the constructor to the initializer function.

```solidity
File: contracts/Balancer.sol

/// @audit initConnectedOFT()
122      constructor(
123          address _routerETH,
124          address _router,
125          address _owner
126      ) Owned(_owner) {
127          if (_router == address(0)) revert RouterNotValid();
128          if (_routerETH == address(0)) revert RouterNotValid();
129          routerETH = IStargateRouter(_routerETH);
130          router = IStargateRouter(_router);
131:     }

```



```solidity
File: contracts/tOFT/BaseTOFT.sol

/// @audit initMultiSell()
50       constructor(
51           address _lzEndpoint,
52           address _erc20,
```

_Trimmed to 38 lines — full report: https://github.com/code-423n4/2022-01-dev-test-repo-findings/issues/361_
