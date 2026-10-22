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
53           IYieldBoxBase _yieldBox,
54           string memory _name,
55           string memory _symbol,
56           uint8 _decimal,
57           uint256 _hostChainID,
58           address payable _leverageModule,
59           address payable _strategyModule,
60           address payable _marketModule,
61           address payable _optionsModule
62       )
63           BaseTOFTStorage(
64               _lzEndpoint,
65               _erc20,
66               _yieldBox,
67               _name,
68               _symbol,
69               _decimal,
70               _hostChainID
71           )
72           ERC20Permit(string(abi.encodePacked("TapiocaOFT-", _name)))
73       {
74           leverageModule = BaseTOFTLeverageModule(_leverageModule);
75           strategyModule = BaseTOFTStrategyModule(_strategyModule);
76           marketModule = BaseTOFTMarketModule(_marketModule);
77           optionsModule = BaseTOFTOptionsModule(_optionsModule);
78:      }

```



```solidity
File: contracts/tOFT/modules/BaseTOFTLeverageModule.sol

/// @audit initMultiSell()
25       constructor(
26           address _lzEndpoint,
27           address _erc20,
28           IYieldBoxBase _yieldBox,
29           string memory _name,
30           string memory _symbol,
31           uint8 _decimal,
32           uint256 _hostChainID
33       )
34           BaseTOFTStorage(
35               _lzEndpoint,
36               _erc20,
37               _yieldBox,
38               _name,
39               _symbol,
40               _decimal,
41               _hostChainID
42           )
43:      {}

```



```solidity
File: contracts/Vesting.sol

/// @audit init()
67       constructor(uint256 _cliff, uint256 _duration, address _owner) {
68           require(_duration > 0, "Vesting: no vesting");
69   
70           cliff = _cliff;
71           duration = _duration;
72           owner = _owner;
73:      }

```



```solidity
File: contracts/markets/bigBang/BigBang.sol

/// @audit init()
98:      constructor() MarketERC20("Tapioca BigBang") {}

```



```solidity
File: contracts/usd0/BaseUSDO.sol

/// @audit initMultiHopBuy()
67       constructor(
68           address _lzEndpoint,
69           IYieldBoxBase _yieldBox,
70           address _owner,
71           address payable _leverageModule,
72           address payable _marketModule,
73           address payable _optionsModule
74       ) BaseUSDOStorage(_lzEndpoint, _yieldBox) ERC20Permit("USDO") {
75           leverageModule = USDOLeverageModule(_leverageModule);
76           marketModule = USDOMarketModule(_marketModule);
77           optionsModule = USDOOptionsModule(_optionsModule);
78   
79           transferOwnership(_owner);
80:      }

```



```solidity
File: contracts/usd0/modules/USDOLeverageModule.sol

/// @audit initMultiHopBuy()
22       constructor(
23           address _lzEndpoint,
24           IYieldBoxBase _yieldBox
25:      ) BaseUSDOStorage(_lzEndpoint, _yieldBox) {}

```


### Assessed type

------------

other
