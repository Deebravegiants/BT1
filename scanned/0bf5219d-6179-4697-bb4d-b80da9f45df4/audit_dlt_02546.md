# [?] MIMSpell - Precission Loss

## Summary
Severity: Unknown
Chain: Ethereum
Component: MIMSpell2
Published: 2024-01-30
Source: https://github.com/SunWeb3Sec/DeFiHackLabs/blob/main/src/test/2024-01/MIMSpell2_exp.sol
Type: defi-exploit-poc

## Details
Lost: ~6,5M
References:
- https://twitter.com/kankodu/status/1752581744803680680
- https://twitter.com/Phalcon_xyz/status/1752278614551216494
- https://twitter.com/peckshield/status/1752279373779194011
- https://app.blocksec.com/explorer/security-incidents

```solidity
contract ContractTest is Test {
    IERC20 private constant MIM = IERC20(0x99D8a9C45b2ecA8864373A26D1459e3Dff1e17F3);
    IUSDT private constant USDT = IUSDT(0xdAC17F958D2ee523a2206206994597C13D831ec7);
    IERC20 private constant Crv3_USD_BTC_ETH = IERC20(0xc4AD29ba4B3c580e6D59105FFf484999997675Ff);
    IERC20 private constant yvCurve_3Crypto_f = IERC20(0x8078198Fc424986ae89Ce4a910Fc109587b6aBF3);
    IERC20 private constant USDC = IERC20(0xA0b86991c6218b36c1d19D4a2e9Eb0cE3606eB48);
    IERC20 private constant WETH = IERC20(0xC02aaA39b223FE8D0A0e5C4F27eAD9083C756Cc2);
    IDegenBox private constant DegenBox = IDegenBox(0xd96f48665a1410C0cd669A88898ecA36B9Fc2cce);
    ICauldronV4 private constant CauldronV4 = ICauldronV4(0x7259e152103756e1616A77Ae982353c3751A6a90);
    ICurvePool private constant MIM_3LP3CRV = ICurvePool(0x5a6A4D54456819380173272A5E8E9B9904BdF41B);
    ICurvePool private constant USDT_WBTC_WETH = ICurvePool(0xD51a44d3FaE010294C616388b506AcdA1bfAAE46);
    Uni_Pair_V3 private constant MIM_USDC = Uni_Pair_V3(0x298b7c5e0770D151e4C5CF6cCA4Dae3A3FFc8E27);
    Uni_Pair_V3 private constant USDC_WETH = Uni_Pair_V3(0x88e6A0c2dDD26FEEb64F039a2c41296FcB3f5640);

    function setUp() public {
        vm.createSelectFork("mainnet", 19_118_659);
        vm.label(address(MIM), "MIM");
        vm.label(address(USDT), "USDT");
        vm.label(address(WETH), "WETH");
        vm.label(address(Crv3_USD_BTC_ETH), "Crv3_USD_BTC_ETH");
        vm.label(address(yvCurve_3Crypto_f), "yvCurve_3Crypto_f");
        vm.label(address(USDC), "USDC");
        vm.label(address(DegenBox), "DegenBox");
        vm.label(address(CauldronV4), "CauldronV4");
        vm.label(address(MIM_3LP3CRV), "MIM_3LP3CRV");
        vm.label(address(USDT_WBTC_WETH), "USDT_WBTC_WETH");
        vm.label(address(MIM_USDC), "MIM_USDC");
        vm.label(address(USDC_WETH), "USDC_WETH");
    }

```

_Trimmed to 38 lines — full report: https://github.com/SunWeb3Sec/DeFiHackLabs/blob/main/src/test/2024-01/MIMSpell2_exp.sol_
